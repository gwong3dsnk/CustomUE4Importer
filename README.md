# CustomUE4Importer
This is a tool I wrote for my previous position where it adheres to the specific project's defined standards and guidelines when it come to asset organization and conventions.  Artists and UI utilize this tool to import source files (fbx, png, tga) into the Unreal Engine 4 editor instead of using UE4's default importer.  This one is customized so it takes note of our custom asset naming conventions, technical art budgets, etc, and creates the uasset.  It then proceeds to automate the setup process by assigning imported textures to new material instances and assigning those material insts to the proper material interface on the imported mesh.  Therefore, the asset is imported and ready to be previewed immediately with little to no user error.

# NOTE THIS!
This code is not usable in its current state.  It was developed for very specific project and much of the logic in this tool conforms to the standards and guidelines of that project.  This code is just here to serve as a window into what I have written.

# What this tool does
User selects 1 or more source assets and adds it to the tool
User imports the assets
The Importer imports the mesh and textures if they don't already exist in the programmatically defined content browser destination path.
The Importer looks at the material slot names to determine what kind of material is expected (opaque, mask, translucent, etc).  Based on this, and the asset type (character, weapon, vehicle etc), it looks up the proper master material and creates a new material instance, naming it after the material slot name.
The Importer parses the imported textures to see what's been imported (base color, mro [metallic, roughness, occlusion], normal, etc) and assigns them to the proper texture 2d interfaces on the mat inst.
Textures are all checked since sometimes they can contain too much blue and UE4 will mistake them as normal maps, giving them normal map compression settings.  This tool ensures that doesn't happen.
Textures all receive proper texture grouping for scalability and memory control.
Material insts are then assigned to the proper material interfaces on the mesh
