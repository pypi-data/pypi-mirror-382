"""
run_r: A Python plugin to execute R scripts and retrieve workspace variables.

This plugin provides a simple interface to run R scripts and extract all variables
from the R workspace after execution.
"""
import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List


def find_rscript() -> Optional[str]:
    """
    Attempt to find Rscript executable on the system.
    
    Returns:
        Path to Rscript executable or None if not found
    """
    # Try common locations on Windows
    if os.name == 'nt':
        common_paths = [
            r"C:\Program Files\R",
            r"C:\Program Files (x86)\R",
            os.path.expanduser(r"~\AppData\Local\Programs\R"),
        ]
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                # Look for R installations
                for r_version in sorted(os.listdir(base_path), reverse=True):
                    rscript_path = os.path.join(base_path, r_version, "bin", "Rscript.exe")
                    if os.path.exists(rscript_path):
                        return rscript_path
    
    # Check if Rscript is in PATH
    rscript_path = shutil.which("Rscript")
    return rscript_path


class RScriptRunner:
    """Execute R scripts and retrieve workspace variables."""
    
    def __init__(self, r_executable: Optional[str] = None):
        """
        Initialize the R script runner.
        
        Args:
            r_executable: Path to Rscript executable. If None, will attempt to find it automatically.
        
        Raises:
            FileNotFoundError: If Rscript executable cannot be found
        """
        if r_executable is None:
            r_executable = find_rscript()
            if r_executable is None:
                raise FileNotFoundError(
                    "Could not find Rscript executable. Please ensure R is installed.\n"
                    "On Windows, R is typically installed in 'C:\\Program Files\\R\\R-x.x.x\\bin\\Rscript.exe'\n"
                    "Or provide the path explicitly: RScriptRunner(r_executable='path/to/Rscript')"
                )
        
        # Verify the executable exists
        if not os.path.exists(r_executable) and shutil.which(r_executable) is None:
            raise FileNotFoundError(
                f"Rscript executable not found at: {r_executable}\n"
                f"Please verify R is installed and the path is correct."
            )
        
        self.r_executable = r_executable
        print(f"Using R executable: {self.r_executable}")
        
        # Check if jsonlite is installed
        self._check_jsonlite()
    
    def _check_jsonlite(self):
        """Check if the jsonlite R package is installed, and install it if not."""
        check_code = 'if (!require("jsonlite", quietly = TRUE)) { install.packages("jsonlite", repos = "https://cran.r-project.org") }'
        try:
            subprocess.run(
                [self.r_executable, "-e", check_code],
                capture_output=True,
                text=True,
                check=True,
                timeout=60
            )
        except subprocess.TimeoutExpired:
            print("Warning: jsonlite package check timed out, proceeding anyway...")
        except Exception as e:
            print(f"Warning: Could not verify jsonlite package: {e}")
    
    def _serialize_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Python data structures to JSON-serializable format.
        
        Handles:
        - pandas DataFrames -> dict of lists (with NaN handling)
        - pandas Series -> list (with NaN handling)
        - numpy arrays -> list (with NaN handling)
        - Basic Python types (int, float, str, bool, list, dict)
        
        Args:
            input_data: Dictionary of Python objects
            
        Returns:
            JSON-serializable dictionary
        """
        import math
        
        def clean_nan(obj):
            """Recursively replace NaN with None for JSON serialization."""
            if isinstance(obj, float):
                if math.isnan(obj) or math.isinf(obj):
                    return None
                return obj
            elif isinstance(obj, dict):
                return {k: clean_nan(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [clean_nan(item) for item in obj]
            else:
                return obj
        
        serializable_data = {}
        
        for key, value in input_data.items():
            # Handle pandas DataFrame
            if hasattr(value, 'to_dict') and hasattr(value, 'columns'):
                # Convert DataFrame to dict and clean NaN values
                df_dict = value.to_dict('list')
                serializable_data[key] = {
                    '_type': 'dataframe',
                    'data': clean_nan(df_dict)
                }
            # Handle pandas Series
            elif hasattr(value, 'to_list'):
                series_list = value.to_list()
                serializable_data[key] = {
                    '_type': 'series',
                    'data': clean_nan(series_list)
                }
            # Handle numpy arrays
            elif hasattr(value, 'tolist'):
                array_list = value.tolist()
                serializable_data[key] = {
                    '_type': 'array',
                    'data': clean_nan(array_list)
                }
            # Handle basic Python types
            else:
                serializable_data[key] = clean_nan(value)
        
        return serializable_data
    
    def run_script(self, script_path: str, input_data: Optional[Dict[str, Any]] = None, verbose: bool = True, debug: bool = False) -> Dict[str, Any]:
        """
        Run an R script and return all workspace variables.
        
        Args:
            script_path: Path to the R script file
            input_data: Optional dictionary of variables to pass to R script.
                       Supports basic Python types and pandas DataFrames.
                       Example: {"df": pandas_dataframe, "threshold": 10}
            verbose: If True, print R script output to console
            debug: If True, keep temporary files and print their paths
            
        Returns:
            Dictionary containing all R workspace variables with their values
            
        Raises:
            FileNotFoundError: If the script file doesn't exist
            RuntimeError: If R script execution fails
        """
        script_path = Path(script_path)
        
        if not script_path.exists():
            raise FileNotFoundError(f"R script not found: {script_path}")
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            output_file = tmp.name
        
        input_file = None
        if input_data:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                input_file = tmp.name
                serializable_data = self._serialize_input_data(input_data)
                json.dump(serializable_data, tmp, indent=2)
                
                if debug:
                    print(f"\nDebug: Input JSON saved to: {input_file}")
                    print(f"Input data preview:")
                    print(json.dumps(serializable_data, indent=2)[:500] + "...")
        
        # Create a temporary R wrapper script
        with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as wrapper_file:
            wrapper_script_path = wrapper_file.name
            
        if debug:
            print(f"Debug: Wrapper script saved to: {wrapper_script_path}")
            print(f"Debug: Output will be saved to: {output_file}")
            
        try:
            # Build R script as list of lines
            wrapper_lines = [
                "# Load jsonlite package",
                "library(jsonlite)",
                "",
                "# Helper function to convert various R objects to JSON-friendly format",
                "convert_to_json_friendly <- function(obj, var_name) {",
                "  # Handle S4 objects (like lme4 models)",
                "  if (isS4(obj)) {",
                "    result <- list(",
                "      '_type' = 'S4_object',",
                "      '_class' = class(obj)[1]",
                "    )",
                "    ",
                "    # Check if it's a merMod object (from lme4)",
                "    if (inherits(obj, 'merMod')) {",
                "      result$model_type <- class(obj)[1]",
                "      ",
                "      # Extract fixed effects",
                "      result$fixed_effects <- data.frame(",
                "        term = names(lme4::fixef(obj)),",
                "        estimate = as.numeric(lme4::fixef(obj)),",
                "        stringsAsFactors = FALSE",
                "      )",
                "      ",
                "      # Extract random effects",
                "      tryCatch({",
                "        ranef_list <- lme4::ranef(obj)",
                "        result$random_effects <- lapply(names(ranef_list), function(grp) {",
                "          re_df <- as.data.frame(ranef_list[[grp]])",
                "          re_df$group_var <- rownames(re_df)",
                "          re_df",
                "        })",
                "        names(result$random_effects) <- names(ranef_list)",
                "      }, error = function(e) NULL)",
                "      ",
                "      # Extract variance-covariance of fixed effects",
                "      tryCatch({",
                "        vcov_mat <- as.matrix(vcov(obj))",
                "        result$vcov_fixed <- list(",
                "          matrix = vcov_mat,",
                "          std_errors = sqrt(diag(vcov_mat))",
                "        )",
                "      }, error = function(e) NULL)",
                "      ",
                "      # Model fit statistics",
                "      tryCatch({",
                "        result$fit_stats <- list(",
                "          AIC = AIC(obj),",
                "          BIC = BIC(obj),",
                "          logLik = as.numeric(logLik(obj)),",
                "          deviance = deviance(obj),",
                "          df_residual = df.residual(obj)",
                "        )",
                "      }, error = function(e) NULL)",
                "      ",
                "      # Extract formula",
                "      tryCatch({",
                "        result$formula <- as.character(formula(obj))",
                "      }, error = function(e) NULL)",
                "      ",
                "      # Number of observations and groups",
                "      tryCatch({",
                "        result$nobs <- nobs(obj)",
                "        result$ngrps <- lme4::ngrps(obj)",
                "      }, error = function(e) NULL)",
                "      ",
                "      # Coefficients summary as dataframe",
                "      tryCatch({",
                "        coef_summary <- coef(summary(obj))",
                "        result$coefficients_summary <- as.data.frame(coef_summary)",
                "      }, error = function(e) NULL)",
                "    }",
                "    ",
                "    return(result)",
                "  }",
                "  ",
                "  # Handle reference classes",
                "  if (is(obj, 'refClass')) {",
                "    return(list(",
                "      '_type' = 'reference_class',",
                "      '_class' = class(obj)[1],",
                "      '_note' = 'Reference classes cannot be fully serialized'",
                "    ))",
                "  }",
                "  ",
                "  # Handle functions",
                "  if (is.function(obj)) {",
                "    return(list(",
                "      '_type' = 'function',",
                "      '_note' = 'Functions cannot be serialized to JSON'",
                "    ))",
                "  }",
                "  ",
                "  # Handle formulas",
                "  if (inherits(obj, 'formula')) {",
                "    return(list(",
                "      '_type' = 'formula',",
                "      'formula' = as.character(obj)",
                "    ))",
                "  }",
                "  ",
                "  # Return as-is for regular objects",
                "  return(obj)",
                "}",
                "",
            ]
            
            # Add input data loading section if input_file exists
            if input_file:
                wrapper_lines.extend([
                    f'if (file.exists("{self._r_quote(input_file)}")) {{',
                ])
                if debug:
                    wrapper_lines.append('  cat("Loading input data...\\n")')
                wrapper_lines.extend([
                    f'  input_list <- fromJSON("{self._r_quote(input_file)}")',
                ])
                if debug:
                    wrapper_lines.append('  cat("Input list names:", paste(names(input_list), collapse=", "), "\\n")')
                wrapper_lines.extend([
                    '  for (var_name in names(input_list)) {',
                    '    var_value <- input_list[[var_name]]',
                    '    # Handle special types',
                    '    if (is.list(var_value) && !is.null(var_value[["_type"]])) {',
                    '      if (var_value[["_type"]] == "dataframe") {',
                    '        df_data <- var_value[["data"]]',
                    '        # Convert NULL to NA in each column',
                    '        for (col_name in names(df_data)) {',
                    '          col_values <- df_data[[col_name]]',
                    '          # Replace NULL with NA',
                    '          col_values <- lapply(col_values, function(x) if (is.null(x)) NA else x)',
                    '          # Unlist to create proper vector',
                    '          df_data[[col_name]] <- unlist(col_values)',
                    '        }',
                    '        # Create data frame with proper column types',
                    '        df_result <- as.data.frame(df_data, stringsAsFactors = FALSE)',
                    '        assign(var_name, df_result, envir = .GlobalEnv)',
                ])
                if debug:
                    wrapper_lines.extend([
                        '        cat("  Assigned dataframe:", var_name, "with", nrow(get(var_name)), "rows\\n")',
                        '        if (TRUE) { print(str(get(var_name))); print(head(get(var_name))) }',
                    ])
                wrapper_lines.extend([
                    '      } else if (var_value[["_type"]] == "series" || var_value[["_type"]] == "array") {',
                    '        vec_data <- unlist(lapply(var_value[["data"]], function(x) if (is.null(x)) NA else x))',
                    '        assign(var_name, vec_data, envir = .GlobalEnv)',
                ])
                if debug:
                    wrapper_lines.append('        cat("  Assigned vector:", var_name, "with length", length(get(var_name)), "\\n")')
                wrapper_lines.extend([
                    '      }',
                    '    } else {',
                    '      # Convert NULL to NA for simple values',
                    '      if (is.null(var_value)) {',
                    '        var_value <- NA',
                    '      }',
                    '      assign(var_name, var_value, envir = .GlobalEnv)',
                ])
                if debug:
                    wrapper_lines.append('      cat("  Assigned variable:", var_name, "=", var_value, "\\n")')
                wrapper_lines.extend([
                    '    }',
                    '  }',
                    '}',
                    '',
                ])
            
            # Add user script execution
            wrapper_lines.extend([
                '# Source the user script',
                'cat("\\nExecuting user script...\\n")',
                f'source("{self._r_quote(str(script_path))}")',
                '',
                '# Get all variables from the workspace',
                'all_vars <- ls(envir = .GlobalEnv)',
            ])
            if debug:
                wrapper_lines.append('cat("\\nAll variables in workspace:", paste(all_vars, collapse=", "), "\\n")')
            
            # Add variable export section
            wrapper_lines.extend([
                '',
                '# Remove our temporary variables and functions',
                'all_vars <- all_vars[!all_vars %in% c("input_list", "var_name", "var_value", "df_data", "col_name", "vec_data", "col_values", "df_result", "convert_to_json_friendly")]',
            ])
            if debug:
                wrapper_lines.append('cat("Variables to export:", paste(all_vars, collapse=", "), "\\n")')
            
            wrapper_lines.extend([
                '',
                '# Create a list to store variables',
                'workspace <- list()',
                '',
                '# Export each variable',
                'for (var_name in all_vars) {',
                '  var_value <- get(var_name, envir = .GlobalEnv)',
                '  ',
                '  tryCatch({',
                '    # Convert to JSON-friendly format',
                '    converted_value <- convert_to_json_friendly(var_value, var_name)',
                '    workspace[[var_name]] <- converted_value',
            ])
            if debug:
                wrapper_lines.append('    cat("  Exported:", var_name, "- Type:", class(var_value)[1], "\\n")')
            wrapper_lines.extend([
                '  }, error = function(e) {',
                '    # If conversion fails, store metadata',
                '    workspace[[var_name]] <- list(',
                '      "_type" = "error",',
                '      "_class" = class(var_value)[1],',
                '      "_error" = e$message',
                '    )',
            ])
            if debug:
                wrapper_lines.append('    cat("  Error exporting:", var_name, "-", e$message, "\\n")')
            wrapper_lines.extend([
                '  })',
                '}',
                '',
            ])
            if debug:
                wrapper_lines.append('cat("\\nWriting output to JSON...\\n")')
            wrapper_lines.extend([
                '# Write to JSON file',
                f'write_json(workspace, "{self._r_quote(output_file)}", auto_unbox = TRUE, digits = NA, na = "null")',
            ])
            if debug:
                wrapper_lines.append('cat("Done!\\n")')
            
            # Join all lines with newlines
            wrapper_code = '\n'.join(wrapper_lines)
            
            # Write the wrapper script
            with open(wrapper_script_path, 'w') as f:
                f.write(wrapper_code)
            
            # Execute the wrapper script
            result = subprocess.run(
                [self.r_executable, wrapper_script_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if verbose or debug:
                if result.stdout:
                    print("\nR Output:")
                    print(result.stdout)
                if result.stderr:
                    print("\nR Warnings/Messages:")
                    print(result.stderr)
            
            if result.returncode != 0:
                error_msg = f"R script execution failed with return code {result.returncode}\n"
                if result.stderr:
                    error_msg += f"Error output:\n{result.stderr}"
                if result.stdout:
                    error_msg += f"\nStandard output:\n{result.stdout}"
                raise RuntimeError(error_msg)
            
            # Read the output JSON file
            if not os.path.exists(output_file):
                raise RuntimeError(f"Output file was not created: {output_file}")
            
            with open(output_file, 'r') as f:
                workspace_vars = json.load(f)
            
            if debug:
                print(f"\nDebug: Returned {len(workspace_vars)} variables")
                print(f"Variable names: {list(workspace_vars.keys())}")
            
            return workspace_vars
            
        finally:
            # Clean up temporary files (unless debug mode)
            if not debug:
                for temp_file in [output_file, wrapper_script_path, input_file]:
                    if temp_file and os.path.exists(temp_file):
                        try:
                            os.unlink(temp_file)
                        except Exception:
                            pass  # Ignore cleanup errors
    
    @staticmethod
    def _r_quote(s: str) -> str:
        """Escape a string for use in R code."""
        return s.replace('\\', '\\\\').replace('"', '\\"')


def run_r_script(script_path: str, r_executable: Optional[str] = None, 
                 input_data: Optional[Dict[str, Any]] = None, verbose: bool = True) -> Dict[str, Any]:
    """
    Convenience function to run an R script and get workspace variables.
    
    Args:
        script_path: Path to the R script file
        r_executable: Path to Rscript executable. If None, will attempt to find it automatically.
        input_data: Optional dictionary of variables to pass to R script.
                   Supports basic Python types and pandas DataFrames.
        verbose: If True, print R script output to console
        
    Returns:
        Dictionary containing all R workspace variables with their values
        
    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]})
        >>> variables = run_r_script("my_script.R", input_data={"my_data": df, "threshold": 10})
        >>> print(variables['result'])
    """
    runner = RScriptRunner(r_executable=r_executable)
    return runner.run_script(script_path, input_data=input_data, verbose=verbose)


def main():
    """CLI entry point for the run-r command."""
    if len(sys.argv) < 2:
        print("Usage: run-r <path_to_r_script>")
        print("   or: python -m run_r <path_to_r_script>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    
    try:
        print(f"Running R script: {script_path}")
        print("=" * 60)
        variables = run_r_script(script_path)
        
        print("\nWorkspace Variables:")
        print("=" * 60)
        for var_name, var_value in variables.items():
            print(f"{var_name}: {var_value}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
