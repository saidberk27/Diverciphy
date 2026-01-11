from flask import Blueprint, jsonify, current_app, request

nodes_bp = Blueprint('nodes', __name__)

def get_node_manager():
    # Expecting the main application to attach the manager (MasterShred or MasterAssemble) to current_app
    return getattr(current_app, 'node_manager', None)

@nodes_bp.route('/api/v1/nodes', methods=['GET'])
def list_nodes():
    manager = get_node_manager()
    if not manager:
        return jsonify({"error": "Node manager not initialized"}), 500
    
    # Assuming manager has 'worker_addresses' list
    workers = getattr(manager, 'worker_addresses', [])
    
    # Enrich with status if possible (mocked or real check)
    nodes = []
    for idx, addr in enumerate(workers):
        nodes.append({
            "id": idx,
            "address": addr,
            "status": "Active", # Default, could be checked via health
            "type": "Worker"
        })
        
    return jsonify({"status": "success", "count": len(nodes), "nodes": nodes}), 200

@nodes_bp.route('/api/v1/nodes/<int:node_id>', methods=['DELETE'])
def delete_node(node_id):
    manager = get_node_manager()
    if not manager:
        return jsonify({"error": "Node manager not initialized"}), 500
        
    workers = getattr(manager, 'worker_addresses', [])
    
    if node_id < 0 or node_id >= len(workers):
        return jsonify({"error": "Node ID out of range"}), 404
        
    # Remove the node
    removed = workers.pop(node_id)
    
    # In a real system, we might need to update env vars or persistence
    return jsonify({"status": "success", "message": f"Node {removed} decomissioned."}), 200

@nodes_bp.route('/api/v1/nodes/<int:node_id>/status', methods=['PUT'])
def update_node_status(node_id):
    # This is a stub implementation as we don't have a complex status state
    data = request.get_json(silent=True)
    status = data.get('status', 'Unknown')
    
    return jsonify({
        "status": "success", 
        "message": f"Node {node_id} status updated to {status} (Mocked)"
    }), 200
