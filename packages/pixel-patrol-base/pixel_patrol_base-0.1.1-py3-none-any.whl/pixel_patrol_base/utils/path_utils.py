from pathlib import Path, PurePosixPath
from typing import Union, List
import logging

logger = logging.getLogger(__name__)

def is_subpath(path_a: Union[str, Path], path_b: Union[str, Path]) -> bool:
    """
    Checks if path_a is a subpath of path_b.
    Paths are resolved to their absolute forms for accurate comparison.
    """
    path_a = Path(path_a).resolve()
    path_b = Path(path_b).resolve()
    try:
        # Check if path_a's parent is path_b, or if path_a is path_b
        # `in` operator for Path objects checks if one is a descendant of another
        return path_a != path_b and path_a.is_relative_to(path_b)
    except ValueError: # Paths on different drives on Windows will raise ValueError for is_relative_to
        return False

def is_superpath(path_a: Union[str, Path], path_b: Union[str, Path]) -> bool:
    """
    Checks if path_a is a superpath (parent) of path_b.
    Paths are resolved to their absolute forms for accurate comparison.
    """
    return is_subpath(path_b, path_a)


def process_new_paths_for_redundancy(validated_paths: List[Path], existing_paths_set: set[Path]) -> set[
    Path]:
    """
    Processes a list of new validated paths, handling redundancy (subpaths/superpaths)
    against a set of existing paths. Returns the updated set of paths.
    """
    final_paths_set = existing_paths_set.copy()

    for new_candidate_path in validated_paths:
        is_subpath_of_existing = False

        # Check against paths already in the final_paths_set (which includes existing + previous new candidates)
        for existing_path_in_set in list(final_paths_set): # Iterate over a copy to allow modification
            # If the new path is a subpath of an existing one, skip it
            if is_subpath(new_candidate_path, existing_path_in_set):
                logger.warning(
                    f"Project Core: Path '{new_candidate_path}' is a subpath of existing project path "
                    f"'{existing_path_in_set}' and will be skipped to avoid redundancy."
                )
                is_subpath_of_existing = True
                break
            # If the new path is a superpath of an existing one, remove the existing (redundant) path
            elif is_superpath(new_candidate_path, existing_path_in_set):
                logger.info(
                    f"Project Core: Path '{new_candidate_path}' is a superpath of existing project path "
                    f"'{existing_path_in_set}'. Removing the subpath."
                )
                final_paths_set.remove(existing_path_in_set)

        if not is_subpath_of_existing:
            # Add the new candidate if it's not a subpath of any other existing/new path
            final_paths_set.add(new_candidate_path)

    return final_paths_set


def find_common_base(paths: List[str]) -> str:
    """
    Finds the common base path among a list of paths.
    """
    if not paths:
        return ""
    if len(paths) == 1:
        return str(Path(paths[0]).parent) + "/"  # Ensure it ends with a slash if it's a directory

    # Convert to Path objects to use their methods
    path_objects = [Path(p) for p in paths]

    # Find the shortest path, as it might be part of the common base
    shortest_path = min(path_objects, key=lambda p: len(str(p)))

    common_parts = []
    for part in shortest_path.parts:
        if all(part in p.parts for p in path_objects):
            common_parts.append(part)
        else:
            break

    # Reconstruct the common base
    common_base = Path(*common_parts)

    # Ensure it ends with the correct separator regarding the system's flavor, e.g. / or \
    system_path_ending = "/" if isinstance(common_base, PurePosixPath) else "\\"

    return str(common_base) + system_path_ending
