from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import heapq
from collections import defaultdict
import json

app = Flask(__name__)
CORS(app)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = 'files'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def build_huffman_tree(data):
    # Calculate frequency of each character
    frequency = defaultdict(int)
    for char in data:
        frequency[char] += 1

    # Create a priority queue to store nodes
    heap = []
    for char, freq in frequency.items():
        heapq.heappush(heap, HuffmanNode(char, freq))

    # Build Huffman tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        internal = HuffmanNode(None, left.freq + right.freq)
        internal.left = left
        internal.right = right
        heapq.heappush(heap, internal)

    return heap[0] if heap else None

def build_huffman_codes(root):
    codes = {}

    def traverse(node, code=""):
        if node:
            if node.char is not None:
                codes[node.char] = code
            traverse(node.left, code + "0")
            traverse(node.right, code + "1")

    traverse(root)
    return codes

def compress_data(data):
    # Build Huffman tree and get codes
    root = build_huffman_tree(data)
    codes = build_huffman_codes(root)

    # Encode the data
    encoded_data = "".join(codes[char] for char in data)

    # Pad encoded data to make it multiple of 8
    padding = 8 - (len(encoded_data) % 8) if len(encoded_data) % 8 != 0 else 0
    encoded_data += "0" * padding

    # Convert binary string to bytes
    compressed_data = bytearray()
    for i in range(0, len(encoded_data), 8):
        byte = encoded_data[i:i+8]
        compressed_data.append(int(byte, 2))

    # Store metadata (codes and padding) for decompression
    metadata = {
        "codes": {char: code for char, code in codes.items()},
        "padding": padding
    }

    return compressed_data, metadata

def decompress_data(compressed_data, metadata):
    # Convert compressed data back to binary string
    binary_data = ""
    for byte in compressed_data:
        binary_data += format(byte, '08b')

    # Remove padding
    binary_data = binary_data[:-metadata["padding"]] if metadata["padding"] > 0 else binary_data

    # Create reverse mapping of codes
    reverse_codes = {code: char for char, code in metadata["codes"].items()}

    # Decode the data
    current_code = ""
    decompressed_data = ""
    for bit in binary_data:
        current_code += bit
        if current_code in reverse_codes:
            decompressed_data += reverse_codes[current_code]
            current_code = ""

    return decompressed_data

@app.route('/files', methods=['GET'])
def list_files():
    files = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if not filename.startswith('metadata_'):
            is_compressed = filename.endswith('.huf')
            files.append({
                'name': filename,
                'compressed': is_compressed
            })
    return jsonify({'files': files})

@app.route('/create', methods=['POST'])
def create_file():
    data = request.json
    if data['userRole'] != 'admin':
        return jsonify({'error': 'Only admin users can create files'}), 403

    filename = data['filename']
    content = data.get('content', '')
    
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        return jsonify({'error': 'File already exists'}), 400

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'message': 'File created successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/read', methods=['GET'])
def read_file():
    filename = request.args.get('filename')
    user_role = request.args.get('userRole')

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Check if file exists
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    # Normal users can only read compressed files
    if user_role == 'normal' and not filename.endswith('.huf'):
        return jsonify({'error': 'Normal users can only read compressed files'}), 403

    try:
        if filename.endswith('.huf'):
            # Read compressed file
            with open(file_path, 'rb') as f:
                compressed_data = f.read()
            
            # Read metadata
            metadata_path = os.path.join(UPLOAD_FOLDER, f"metadata_{filename[:-4]}")
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Decompress data
            content = decompress_data(compressed_data, metadata)
        else:
            # Read regular file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        
        return jsonify({'content': content})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save_file():
    data = request.json
    if data['userRole'] != 'admin':
        return jsonify({'error': 'Only admin users can modify files'}), 403

    filename = data['filename']
    content = data['content']
    
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({'message': 'File saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete', methods=['DELETE'])
def delete_file():
    data = request.json
    if data['userRole'] != 'admin':
        return jsonify({'error': 'Only admin users can delete files'}), 403

    filename = data['filename']
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        os.remove(file_path)
        # If it's a compressed file, also remove its metadata
        if filename.endswith('.huf'):
            metadata_path = os.path.join(UPLOAD_FOLDER, f"metadata_{filename[:-4]}")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
        return jsonify({'message': 'File deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/compress', methods=['GET'])
def compress_file():
    filename = request.args.get('filename')
    user_role = request.args.get('userRole')

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    if user_role != 'admin':
        return jsonify({'error': 'Only admin users can compress files'}), 403

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()

        # Compress the data
        compressed_data, metadata = compress_data(data)

        # Save compressed file
        compressed_path = os.path.join(UPLOAD_FOLDER, f"{filename}.huf")
        with open(compressed_path, 'wb') as f:
            f.write(compressed_data)

        # Save metadata
        metadata_path = os.path.join(UPLOAD_FOLDER, f"metadata_{filename}")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)

        return jsonify({'message': 'File compressed successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 