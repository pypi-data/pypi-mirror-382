
# FIG1 = [
#     ('Set', "folder=basic"),
#     ('Basic', None),
#     ('Plot', None),
#     ('Save', None),
# 3]

FIG1b = [
    ('Set', "folder=basic"),
    ('Load', 'basic/Save'),
    ('WeightedSum', None),
    ('Ground', None),
    ('Camera', 75),
    ('Render', None),
]

# Basic
blender --python generate_terrain.py -- --save-dir basic --modules Basic Plot Save
blender --python generate_terrain.py -- --save-dir basic --modules Load:basic/Save WeightedSum:[10,3,0.3] Ground Camera:75 Render:b.png

# Octaves
python generate_terrain.py --save-dir octaves --modules Octaves Plot Save
blender --python generate_terrain.py -- --save-dir octaves --modules Load:octaves/Save Random:weights WeightedSum Save:Save2 Ground Camera:75 Holdout Render
blender --python generate_terrain.py -- --save-dir octaves --modules Load:octaves/Save Random:weights WeightedSum Ground Camera:75 Holdout Render:b.png

# Rocks
python generate_terrain.py --save-dir rocks --modules Rocks Plot Save
blender --python generate_terrain.py -- --save-dir rocks --modules Load:rocks/Save Combine Ground Camera:75 Render
blender --python generate_terrain.py -- --save-dir rocks --modules Load:rocks/Save Combine Load:octaves/Save2 Combine Ground Camera:75 Render:with_terrain.png

# Holes
python generate_terrain.py --save-dir holes --modules Holes Plot Save
blender --python generate_terrain.py -- --save-dir holes --modules Load:holes/Save Combine Ground Camera:75 Render
blender --python generate_terrain.py -- --save-dir holes --modules Load:holes/Save Combine Load:octaves/Save2 Combine Ground Camera:75 Render:with_terrain.png

# Generating functions
python generate_terrain.py --save-dir gen_func --modules Gaussian Step Donut Plane Sphere Cube SmoothStep Sine Plot Save

# Generating functions 2
blender --python generate_terrain.py -- --save-dir gen_fun_2 --modules Random:10 Gaussian Combine Ground Camera:75 Render
blender --python generate_terrain.py -- --save-dir gen_fun_2 --modules SetDistribution:'height=uniform(-5,5)' Random:10 Gaussian Combine Ground Camera:75 Render:b.png

# Distributions
blender --python generate_terrain.py -- --save-dir 2Dsampling --modules Donut:"dict(width=40)" AsProbability Random:10 Sphere Combine Ground Camera:75 Render
blender --python generate_terrain.py -- --save-dir 2D_lookup --modules Plane:"dict(pitch_deg=10)" AsLookupFor:height Random:10 SaveObstacles Gaussian Combine Ground Camera:75 Render:lookup.png
python generate_terrain.py --save-dir plot_obstacles --modules LoadObstacles:2D_lookup/SaveObstacles/obstacles.npz PlotObstacles

# Function
blender --python generate_terrain.py -- --save-dir function --modules Function:'5*(x/np.max(x))**2+np.sin(y/2)' Ground Camera:65 Render

# Blender
blender --python generate_terrain.py -- --save-dir blender --modules Load:octaves/Save LoadObstacles:2D_lookup/SaveObstacles/obstacles.npz AddMeshObjects Ground Camera:75 Render Camera:top Depth Save
blender --python generate_terrain.py -- --save-dir blender --modules Load:blender/Save Ground Camera:75 Render:combined.png

# Blender 2
blender --python generate_terrain.py -- --save-dir blender --modules Load:blender/Save Ground ImageTexture:plot_obstacles/PlotObstacles/obstacles_0.png Camera:75 Render:texture1.png
blender --python generate_terrain.py -- --save-dir blender --modules Load:octaves/Save LoadObstacles:2D_lookup/SaveObstacles/obstacles.npz AddMeshObjects Ground Camera:top RenderSegmentation:segmentation_top.png
blender --python generate_terrain.py -- --save-dir blender --modules Load:blender/Save Ground ImageTexture:blender/RenderSegmentation/segmentation_top.png Camera:75 Render:texture2.png

# Loop figures
blender --python generate_terrain.py -- --save-dir loop --modules Loop:2x2 Basic WeightedSum Ground EndLoop Camera:75 Render:1.png
blender --python generate_terrain.py -- --save-dir loop --modules Loop:2x2 Seed:2 Basic WeightedSum Ground EndLoop Camera:75 Render:2.png
blender --python generate_terrain.py -- --save-dir loop --modules Loop:2x2 Seed:2 Basic WeightedSum EndLoop Stack Ground Camera:75 Render:3.png

# Random and Loop
# blender --python generate_terrain.py -- --save-dir loop --modules Loop:2x2 Random:5 Gaussian Combine Ground EndLoop Camera:75 Render:4.png
# blender --python generate_terrain.py -- --save-dir loop --modules Random:20 Loop:2x2 Gaussian Combine Ground EndLoop Camera:75 Render:5.png

# Roughness and slop
python generate_terrain.py --save-dir slope_plot --modules Loop:persistence=linspace[0,0.99,100] Octaves:"dict(random_amp=0.0)" WeightedSum Slope Roughness LogData
python generate_terrain.py --save-dir slope_plot --modules LoadData:slope_plot/LogData/data.npz PlotScatter

# Loop over Octaves parameters
python generate_terrain.py --save-dir slope_plot2 --modules Loop:random_amp=linspace[0,0.5,6] Loop:persistance=linspace[0.5,0.7,21] Octaves WeightedSum Slope Roughness LogData
python generate_terrain.py --save-dir slope_plot2 --modules LoadData:slope_plot2/LogData/data.npz PlotScatter:"dict(color='random_amp',cmap='cet_bjy')"

# 500 Octaves terrains
python generate_terrain.py --save-dir proxy-roughness --modules Loop:num_octaves=arange[1,11] Loop:50 Octaves Roughness CombineRoughness WeightedSum Roughness LogData
python generate_terrain.py --save-dir proxy-roughness --modules LoadData:proxy-roughness/LogData/data.npz PlotScatter:"dict(color='num_octaves',cmap='cet_bjy',grid=True)"

# Roughness and slope grid
python generate_terrain.py --save-dir slope_grid --modules Octaves Save
blender --python generate_terrain.py -- --save-dir slope_grid --modules Loop:target_slope_deg=linspace[5,20,4] Loop:target_roughness=linspace[1.01,1.07,4] Load:slope_grid/Save Octaves:"dict(random_amp=0.0,random_sign=False,only_generate_weights=True)" Slope SetSlope Roughness SetRoughness WeightedSum Ground Camera:65 Render ClearScene ClearTerrain

# Number of rocks
python generate_terrain.py --save-dir rocksize_fraction --module Resolution:10 Loop:fraction=linspace[0.5,0.95,10] Loop:rock_size=linspace[0.5,4,15] Rocks FindRocks SurfaceStructure LogData
python generate_terrain.py --save-dir rocksize_fraction --module LoadData PlotScatter:"dict(color='fraction',cmap='cet_bjy',grid=True)"

# FindRocks and image texture
blender --python generate_terrain.py -- --save-dir rocksize_fraction --module Resolution:10 Loop:fraction=linspace[0.5,0.8,4] Loop:rock_size=linspace[1,4,4] Rocks FindRocks SurfaceStructure PlotObstacles ClearScene Ground ImageTexture Camera:45 Holdout Render --settings exportmode:True

# Plot height intervals
python generate_terrain.py --save-dir height_intervals --module Resolution:10 Loop:rock_size=linspace[0.5,4,200] Rocks FindRocks SurfaceStructure LogData
python generate_terrain.py --save-dir height_intervals --module LoadData PlotScatter:"dict(grid=True)"


# Spatial distribution of rocks
blender --python generate_terrain.py -- --save-dir spatial --module Resolution:10 Basic:10 Scale:10 Clip Plot AsFactor Rocks Combine Scale FindRocks SurfaceStructure PlotObstacles Ground ImageTexture Camera:65 Render --settings exportmode:True
blender --python generate_terrain.py -- --save-dir spatial --module Resolution:10 Plane Ground ImageTexture:spatial/Plot/terrain_temp_00000_0.png Camera:65 Holdout Render:mask.png

# Rock position restrictions and random_shift
python generate_terrain.py --save-dir hexagon --module Loop:1000 Rocks:"dict(fraction=0.9,rock_size=4)" EndLoop Combine:Max Plot


if __name__ == "__main__":
    """
    Script entry point for plot/renders of example configurations

    Usage:
    Run the script directly with Python:
            python -m artificial_terrains.examples

    # Note: for the reason of my probably not handling all imports
    # correctly, the following does not work:
    python artificial_terrains_cfg.py

    Or run it inside Blender in background mode:
        blender --python artificial_terrains_cfg.py --background

    Notes:
    - Rendering requires Blender and artificial_terrains package
    """
    current_module = globals()
    configs = {
        name: value for name, value in current_module.items()
        if name.isupper() and isinstance(value, list)
    }

    for name, config in configs.items():
        print(f"\n=== Running config: {name} ===")
        import artificial_terrains as at

        base_cfg = [
            ('Size', [30, 30]),
            ('GridSize', [300, 300]),
        ]

        plot_cfg = [
            ('Plot', {'filename_base': f'{name}',
                      'folder': 'example_plots'}),
        ]

        render_cfg = [
            # ('ClearScene', None),
            ('BasicSetup', None),
            ('Holdout', None),
        ]

        # Run script for plots
        at.run(base_cfg + config, verbose=True)

        # Try to run as blender script
        try:
            at.run(base_cfg + config + render_cfg, verbose=True)
        except ModuleNotFoundError:
            pass
