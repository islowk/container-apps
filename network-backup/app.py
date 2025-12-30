from flask import Flask, request, jsonify
import logging
from datetime import datetime, timezone

from src.helper.auth import get_credential, preflight_check
from src.helper.utils import safe_name, get_subscriptions
from src.storage.compression import compress_backup
from src.storage.storage import upload_to_blob
from src.storage.backup import backup_network_resources

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Container Apps"""
    return jsonify({"status": "healthy"}), 200


@app.route('/network_backup_trigger', methods=['POST', 'GET'])
def network_backup_trigger():
    """
    Network backup endpoint - triggered by Logic App monthly schedule
    Accepts optional 'target_sub' parameter to backup specific subscription
    """
    logger.info('Network Backup trigger received')

    # Run preflight checks
    try:
        preflight_check()
    except Exception as e:
        error_msg = f"Preflight check failed: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "status": "failed",
            "message": error_msg
        }), 500

    # Get optional target_sub parameter
    target_sub = None
    if request.method == 'POST':
        if request.is_json:
            target_sub = request.json.get('target_sub')
        else:
            target_sub = request.form.get('target_sub')
    elif request.method == 'GET':
        target_sub = request.args.get('target_sub')

    # Generate timestamp once for the entire backup run
    DATESTAMP = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")

    response_data = {
        "timestamp": DATESTAMP,
        "status": "success",
        "subscriptions": [],
        "message": ""
    }

    try:
        credential = get_credential()
        logger.info("Authentication successful")

        subs = get_subscriptions(credential, target_sub)
        logger.info(f"Found {len(subs)} subscription(s) to backup")

        for sub in subs:
            logger.info(f"Starting backup for subscription: {sub.display_name}")

            # Backup network resources
            backup_dir = backup_network_resources(
                credential,
                sub.subscription_id,
                sub.display_name,
                DATESTAMP
            )

            # Compress backup
            zip_buffer = compress_backup(backup_dir)

            # Upload to blob storage with new folder structure
            blob_name = f"{DATESTAMP}/{safe_name(sub.display_name)}_network_backup.zip"
            upload_to_blob(zip_buffer, blob_name)

            logger.info(f"Backup completed for subscription: {sub.display_name}")

            # Add subscription details to response
            response_data["subscriptions"].append({
                "subscription_id": sub.subscription_id,
                "display_name": sub.display_name,
                "backup_blob": blob_name
            })

        response_data["message"] = f"Backup completed successfully for {len(subs)} subscription(s)!"
        return jsonify(response_data), 200

    except Exception as e:
        error_msg = f"Fatal error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        response_data["status"] = "failed"
        response_data["message"] = error_msg
        return jsonify(response_data), 500


if __name__ == '__main__':
    # For local testing - Container Apps will use gunicorn
    app.run(host='0.0.0.0', port=8000, debug=False)
