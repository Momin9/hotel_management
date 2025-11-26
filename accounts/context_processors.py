from .models import SiteConfiguration

def site_config(request):
    """
    Context processor to make site configuration available in all templates
    """
    try:
        config = SiteConfiguration.get_instance()
        return {
            'site_config': config,
        }
    except Exception:
        # Fallback in case of database issues
        return {
            'site_config': {
                'company_name': 'AuraStay',
                'company_logo': None,
                'site_title': 'AuraStay - Hotel Management System',
                'site_description': "The world's most advanced hotel management platform"
            }
        }