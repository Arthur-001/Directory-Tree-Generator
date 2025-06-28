import os
import errno
import io
import fnmatch

# Global variables to customize the tree generation
tree_depth = 1  # Controls how many levels of subdirectories to show (0 = root only, 1 = root + one level, 2 = root + two levels, etc.)
show_subdirectory_files = True  # Controls whether to show files in subdirectories (True = show all files, False = only show directories)
sort_alphabetically = True  # Controls whether to sort files and folders alphabetically (True = sort, False = no sorting)

# Emoji and indentation configuration
root_emoji = "🌐"  # Emoji for root directory, set to "" to disable
subdir_emoji = "📁"  # Emoji for subdirectories, set to "" to disable
extra_indent = 0  # Number of spaces to add for items within subdirectories when emoji is enabled

# Filtering options
exclude_folders = [
    "node_modules", ".git", "venv", "__pycache__", 
    "env", "Lib", "Scripts", "Include", "fletApp",
    ".cursor", "Archived", "tests"
]  # List of folders to exclude completely

# New configuration for directory-specific folder exclusions
exclude_folders_in_dirs = {
    "logs": "*",          # Exclude all folders in 'logs' directory
    "temp": "*",          # Exclude all folders in 'temp' directory
    "data": ["raw*", "processed*"],  # Exclude specific folder patterns in 'data' directory
    "src": ["test*", "temp*"],    # Exclude folders starting with 'test' or 'temp' in 'src' directory
    "docs": ["draft*", "temp*"],   # Exclude folders starting with 'draft' or 'temp' in 'docs'
    "Fine-Tuned Models": "*"
}  # Dictionary of directory names and folder patterns to exclude

# New configuration for directory-specific file exclusions
exclude_files_in_dirs = {
    "logs": "*",          # Exclude all files in 'logs' directory
    "temp": "*",          # Exclude all files in 'temp' directory
    "data": ["*.csv", "*.json"],  # Exclude specific file types in 'data' directory
    "src": ["*.pyc", "*.pyo"],    # Exclude compiled files in 'src' directory
    "docs": ["draft*", "temp*"]   # Exclude files starting with 'draft' or 'temp' in 'docs'
}  # Dictionary of directory names and file patterns to exclude

# New configuration for directories where files should not be shown
hide_files_in_dirs = [
    "tests",      # Hide all files in test directories
    "examples",   # Hide all files in example directories
    "samples",    # Hide all files in sample directories
    "templates",   # Hide all files in template directories
    "evaluationResults",
    "hospital_assistant_index"
]  # List of directory names where files should not be shown

exclude_patterns = [
    "#", "~"   # Exclude temporary files
]  # Characters or patterns to exclude in both files and folders

# New specific character exclusions for files and folders
exclude_file_with_char = [
    "$",   # System files
    "@",   # Temporary files
    "&",   # Special files
    "%",    # Generated files
    "directory-structure.txt"
]  # Characters that if present anywhere in a filename will exclude it

exclude_folder_with_char = [
    "+",   # Special folders
    "!",   # System folders
    "^",   # Temporary folders
    "*",    # Generated folders
    "test_run_"
]  # Characters that if present anywhere in a folder name will exclude it

exclude_extensions = [
    ".pyc", ".pyo",  # Python compiled files
    ".log", ".tmp",  # Log and temporary files
    ".cache"         # Cache files
]  # File extensions to exclude

# File filtering options
show_files = True  # Set to True to include files in the output, False for directories only
min_file_size = 0  # Minimum file size in bytes (0 = no minimum)
max_file_size = float('inf')  # Maximum file size in bytes (float('inf') = no maximum)

only_show_files_with_specific_char_indir = {}
only_show_folders_with_specific_char_indir = {}
# New: recursive rules
only_show_files_with_specific_char_indir_recursive = {}
only_show_folders_with_specific_char_indir_recursive = {}

def matches_pattern(filename, pattern):
    """
    Check if a filename matches a pattern (supports basic wildcards * and ?), or if the pattern is a substring (case-insensitive).
    
    Args:
        filename (str): The filename to check
        pattern (str): The pattern to match against
        
    Returns:
        bool: True if the filename matches the pattern
    """
    import fnmatch
    if fnmatch.fnmatch(filename, pattern):
        return True
    # Substring match (case-insensitive)
    if pattern.lower() in filename.lower():
        return True
    return False

def should_include_item(item, path, parent_dir=None, root_dir=None):
    """
    Determine if an item should be included in the tree based on filtering rules.
    
    Args:
        item (str): The name of the file or folder
        path (str): The full path to the item
        parent_dir (str): The name of the parent directory (if any)
        root_dir (str): The root directory for the tree (for root file logic)
        
    Returns:
        bool: True if the item should be included, False otherwise
    """
    # Directory-specific rules
    if parent_dir:
        # Exclude folders in specific directories
        if os.path.isdir(path) and parent_dir in exclude_folders_in_dirs:
            patterns = exclude_folders_in_dirs[parent_dir]
            if patterns == "*":
                return False
            if any(matches_pattern(item, pattern) for pattern in patterns):
                return False
        # Exclude files in specific directories
        if os.path.isfile(path) and parent_dir in exclude_files_in_dirs:
            patterns = exclude_files_in_dirs[parent_dir]
            if patterns == "*":
                return False
            if any(matches_pattern(item, pattern) for pattern in patterns):
                return False
    # Check for excluded patterns (applies to both files and folders)
    if any(item.startswith(pattern) for pattern in exclude_patterns):
        return False
        
    # If it's a directory, always show unless excluded by other rules
    if os.path.isdir(path):
        # Check if folder name is in exclude list
        if item in exclude_folders:
            return False
        # Check if folder name contains any excluded characters
        if any(char in item for char in exclude_folder_with_char):
            return False
            
        # Check directory-specific folder exclusions
        if parent_dir and parent_dir in exclude_folders_in_dirs:
            patterns = exclude_folders_in_dirs[parent_dir]
            if isinstance(patterns, str) and patterns == "*":
                return False
            if isinstance(patterns, list):
                if any(matches_pattern(item, pattern) for pattern in patterns):
                    return False
                    
        # --- Recursive include-only-folder rules ---
        # If this is a directory, check up the directory tree for recursive include-only-folder rules
        current_path = os.path.abspath(path)
        ancestors = []
        while True:
            parent = os.path.dirname(current_path)
            if parent == current_path:
                break
            ancestors.append(os.path.basename(parent))
            current_path = parent
        # Check all ancestors for recursive include-only-folder rules
        for ancestor in ancestors:
            patterns = only_show_folders_with_specific_char_indir_recursive.get(ancestor, [])
            if patterns:
                # patterns is a list of (pattern, recursive) or just pattern if legacy
                for idx, pattern in enumerate(patterns):
                    # If legacy, treat as not recursive
                    if isinstance(pattern, str):
                        pat = pattern
                        recursive = False
                    elif isinstance(pattern, list) or isinstance(pattern, tuple):
                        pat, recursive = pattern
                    else:
                        continue
                    if recursive:
                        if not matches_pattern(item, pat):
                            return False
        # Also check direct parent for non-recursive include-only-folder rules
        if parent_dir in only_show_folders_with_specific_char_indir:
            patterns = only_show_folders_with_specific_char_indir[parent_dir]
            if not any(matches_pattern(item, pattern) for pattern in patterns):
                return False
        # --- End recursive include-only-folder rules ---
            
        return True
    
    # If it's a file, apply file-specific filters
    if os.path.isfile(path):
        # Correct root file logic: parent dir of file must match root_dir
        if root_dir is not None:
            is_root_file = os.path.dirname(os.path.abspath(path)) == os.path.abspath(root_dir)
        else:
            is_root_file = os.path.dirname(path) == os.path.dirname(os.path.abspath(__file__))
        
        # Always show files in root directory, but for subdirectories respect show_subdirectory_files setting
        if not is_root_file and not show_subdirectory_files:
            return False
            
        # Check if parent directory is in hide_files_in_dirs
        if parent_dir and parent_dir in hide_files_in_dirs:
            return False
            
        # Check directory-specific file exclusions
        if parent_dir and parent_dir in exclude_files_in_dirs:
            patterns = exclude_files_in_dirs[parent_dir]
            if isinstance(patterns, str) and patterns == "*":
                return False
            if isinstance(patterns, list):
                if any(matches_pattern(item, pattern) for pattern in patterns):
                    return False
        
        # Check if file contains any excluded characters
        if any(char in item for char in exclude_file_with_char):
            return False
            
        # Check file extension
        if any(item.endswith(ext) for ext in exclude_extensions):
            return False
            
        # Check file size if specified
        try:
            size = os.path.getsize(path)
            
            # Handle max_file_size type conversion
            max_size = max_file_size
            if isinstance(max_size, str) and max_size == "inf":
                max_size = float('inf')
            elif isinstance(max_size, str):
                try:
                    max_size = float(max_size)
                except ValueError:
                    max_size = float('inf')
            
            if not (min_file_size <= size <= max_size):
                return False
        except OSError:
            return False  # If we can't get the file size, exclude it
            
    return True
def generate_directory_tree(root_dir, output_file="directory-structure.txt"):
    buffer = io.StringIO()
    try:
        # Get just the folder name instead of full path
        root_name = os.path.basename(root_dir.rstrip(os.path.sep))
        if not root_name:  # In case the path ends with a separator
            root_name = os.path.basename(os.path.dirname(root_dir))
        
        # Add root emoji if configured
        buffer.write(f"{root_emoji}{root_name}\n")

        def _generate_tree(current_dir, prefix="", is_last=False, level=0, is_in_subdir=False):
            if level > tree_depth:
                return

            try:
                # Get all items and separate directories and files
                items = os.listdir(current_dir)
                dirs = []
                files = []
                
                current_dir_name = os.path.basename(current_dir)
                
                for item in items:
                    path = os.path.join(current_dir, item)
                    if not should_include_item(item, path, current_dir_name, root_dir):
                        continue
                        
                    if os.path.isdir(path):
                        dirs.append(item)
                    elif os.path.isfile(path) and show_files:
                        files.append(item)
                
                # Sort directories and files separately if sorting is enabled
                if sort_alphabetically:
                    dirs.sort(key=str.lower)  # Case-insensitive sorting
                    files.sort(key=str.lower)  # Case-insensitive sorting
                
                # Combine sorted directories and files
                all_items = dirs + files
                
                if not all_items:
                    return

                for index, item in enumerate(all_items):
                    is_last_item = index == len(all_items) - 1
                    path = os.path.join(current_dir, item)
                    is_dir = os.path.isdir(path)

                    # Determine if we need extra indentation
                    extra_spacing = " " * extra_indent if is_in_subdir and subdir_emoji else ""

                    # Prepare the line prefix
                    line_prefix = prefix + ('└───' if is_last_item else '├───')

                    if is_dir:
                        # Always show subdirectory emoji for directories (except root)
                        buffer.write(f"{line_prefix}{subdir_emoji}{item}\n")
                    else:  # Files
                        buffer.write(f"{line_prefix}{extra_spacing}{item}\n")

                    if is_dir:
                        # Prepare the prefix for children
                        new_prefix = prefix + ('    ' if is_last_item else '│   ')
                        # Pass is_in_subdir=True for the next level if we're in a subdirectory or at root level
                        _generate_tree(path, new_prefix, is_last_item, level + 1, True)

            except OSError as e:
                error_msg = "Access Denied" if e.errno == errno.EACCES else str(e)
                buffer.write(f"{prefix}{'└───' if is_last else '├───'}{error_msg}\n")
                return

        # Start the recursive generation from the root directory
        _generate_tree(root_dir)

    except Exception as e:
        buffer.write(f"Error generating tree: {e}")

    result = buffer.getvalue()
    
    # Write to file if requested
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result)
        except OSError as e:
            result += f"\nError writing to file: {output_file} - {e}"
    
    return result

if __name__ == "__main__":
    # Get the directory where the script is located
    script_directory = os.path.dirname(os.path.abspath(__file__))
    generate_directory_tree(script_directory)  # Generate the tree
    print(f"Directory tree generated and saved to directory-structure.txt")