import numpy as np
import neuroboros as nb
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# Load the mapping data (ico128)
mapping_data = np.load("/Users/elizabethli/.neuroboros-data/core/2d_plotting_data/onavg-ico128_to_inflated_image.npy")
original_height, original_width = mapping_data.shape
print(f"Mapping data shape: {mapping_data.shape}")  # (1560, 1728)

#load lookup tables
lookup_table_ico8 = np.load("/Users/elizabethli/vscode/haxbyLab/visualizationProject/lookup_tables/ico128_ico8_LUT.npy")
lookup_table_ico16 = np.load("/Users/elizabethli/vscode/haxbyLab/visualizationProject/lookup_tables/ico128_ico16_LUT.npy")
lookup_table_ico32 = np.load("/Users/elizabethli/vscode/haxbyLab/visualizationProject/lookup_tables/ico128_ico32_LUT.npy")
lookup_table_ico64 = np.load("/Users/elizabethli/vscode/haxbyLab/visualizationProject/lookup_tables/ico128_ico64_LUT.npy")

# Initialize global variables for display size
display_width = None
display_height = None

scale_x = 1  # Default values before scaling is set
scale_y = 1


def calculate_scaling_factors():
    global scale_x, scale_y
    if display_width is not None and display_height is not None:
        scale_x = original_width / display_width
        scale_y = original_height / display_height
        print(f"Scaling factors: scale_x={scale_x}, scale_y={scale_y}")

#for when the window is resized
@app.route('/update_display_size', methods=['POST'])
def update_display_size():
    global display_width, display_height
    try:
        data = request.json
        display_width = int(data.get('width'))
        display_height = int(data.get('height'))

        print(f"Received new display size: width={display_width}, height={display_height}")

        # Update scaling factors
        calculate_scaling_factors()
        return jsonify({'status': 'success'})
    except Exception as e:
        print(f"Error updating display size: {e}")
        return jsonify({'error': str(e)}), 500



def get_vertex_from_mapping(mouse_x, mouse_y, mapping_data):
    if 0 <= mouse_y < mapping_data.shape[0] and 0 <= mouse_x < mapping_data.shape[1]:
        vertex = mapping_data[mouse_y, mouse_x]
        if vertex != -1: #valid vertex index
            return vertex
        else: 
            return None #mouse is over non-brain area
    return None #mouse is outside image bounds

#get vertex coodinates from mouse coordinates  
@app.route('/get_vertex', methods=['GET'])
def get_vertex():
    try:
        x = float(request.args.get('x'))
        y = float(request.args.get('y'))

        #rescale mouse coordinates to original dimensions
        mouse_x_original = int(x * scale_x)
        mouse_y_original = int(y * scale_y)

        print(f"Raw mouse coordinates: ({x}, {y})")
        print(f"Scaled coordinates: ({mouse_x_original}, {mouse_y_original})")

        #fetch ico128 vertex index
        vertex = get_vertex_from_mapping(mouse_x_original, mouse_y_original, mapping_data)

        if vertex is not None:
            vertex = int(vertex)
            ico8_vertex = int(lookup_table_ico8[vertex])
            ico16_vertex = int(lookup_table_ico16[vertex])
            ico32_vertex = int(lookup_table_ico32[vertex])
            ico64_vertex = int(lookup_table_ico64[vertex])
        else:
            ico8_vertex = ico16_vertex = ico32_vertex = ico64_vertex = None

        return jsonify({
            'ico8': ico8_vertex,
            'ico16': ico16_vertex,
            'ico32': ico32_vertex,
            'ico64': ico64_vertex,
            'ico128': vertex
        })
        
    except Exception as e:
        print(f"Error updating display size: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

