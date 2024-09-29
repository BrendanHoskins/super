from models.user.user import User

def get_user_integrations(user_id):
    user = User.objects(id=user_id).first()
    
    # Define default integrations
    integrations = {
        'slack': {
            'enabled': False,
            'component': 'SlackBox',
            'installation': None
        }
        # Add other default integrations here as needed
    }
    
    if user:
        slack_integration = user.thirdPartyIntegrations.get('slack')
        if slack_integration:
            integrations['slack'] = {
                'enabled': slack_integration.enabled,
                'installation': slack_integration.installation.to_dict() if slack_integration.installation else None
            }
    
    return integrations
