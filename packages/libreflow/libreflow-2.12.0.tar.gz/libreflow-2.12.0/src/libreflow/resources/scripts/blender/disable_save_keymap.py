import sys
import bpy
from bpy.app.handlers import persistent

original_filepath = bpy.path.abspath(bpy.data.filepath)


def is_original_filepath():
    return (len(original_filepath) > 0
            and bpy.path.abspath(bpy.data.filepath) == original_filepath)


@persistent
def check_working_copy(filepath):
    """Run handler when loading file, decide whether to enable save."""
    import importlib
    warnings = None
    try:
        warnings = importlib.import_module("lfs_scene_builder.utils.warnings")
    except ModuleNotFoundError:
        pass
    if warnings is None:
        try:
            warnings = importlib.import_module("lfs-scene-builder.utils.warnings")
        except ModuleNotFoundError:
            pass

    if warnings is None:
        return

    if is_original_filepath():
        warnings.warnings["outdated_working_copy"] = {
            "side": "L",
            "message": ("Your working copy is outdated.\n"
                        "There is a more recent version than your file.\n"
                        "Check the history in Libreflow."),
        }
        bpy.ops.lfs.scene_builder_display_warning(do_enable=True)
    elif "outdated_working_copy" in warnings.warnings:
        del warnings.warnings["outdated_working_copy"]


def register():
    argv = sys.argv
    if 'working_copy' in argv:
        bpy.app.handlers.load_post.append(check_working_copy)
        check_working_copy(bpy.data.filepath)


if __name__ == "__main__":
    register()
