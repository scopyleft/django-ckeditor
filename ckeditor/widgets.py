from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.utils import simplejson

from django.core.exceptions import ImproperlyConfigured
from django.forms.util import flatatt
from copy import deepcopy

json_encode = simplejson.JSONEncoder().encode

DEFAULT_CONFIG = {
    'skin': 'kama',
    'toolbar': 'Full',
    'height': 291,
    'width': 618,
    'filebrowserWindowWidth': 940,
    'filebrowserWindowHeight': 747,
}

class CKEditorWidget(forms.Textarea):
    """
    Widget providing CKEditor for Rich Text Editing.
    Supports direct image uploads and embed.
    """
    class Media:
        try:
            js = (
                settings.STATIC_URL + 'ckeditor/ckeditor/ckeditor.js',
            )
        except AttributeError:
            raise ImproperlyConfigured("django-ckeditor requires CKEDITOR_MEDIA_PREFIX setting. This setting specifies a URL prefix to the ckeditor JS and CSS media (not uploaded media). Make sure to use a trailing slash: CKEDITOR_MEDIA_PREFIX = '/media/ckeditor/'")

    def __init__(self, config_name='default', *args, **kwargs):
        super(CKEditorWidget, self).__init__(*args, **kwargs)
        # Setup config from defaults.
        self.config = DEFAULT_CONFIG

        # Try to get valid config from settings.
        configs = getattr(settings, 'CKEDITOR_CONFIGS', None)
        if configs != None: 
            if isinstance(configs, dict):
                # Make sure the config_name exists.
                if configs.has_key(config_name):
                    config = configs[config_name]
                    # Make sure the configuration is a dictionary.
                    if not isinstance(config, dict):
                        raise ImproperlyConfigured('CKEDITOR_CONFIGS["%s"] setting must be a dictionary type.' % config_name)
                    # Override defaults with settings config.
                    self.config = deepcopy(config)
                else:
                    raise ImproperlyConfigured("No configuration named '%s' found in your CKEDITOR_CONFIGS setting." % config_name)
            else:
                raise ImproperlyConfigured('CKEDITOR_CONFIGS setting must be a dictionary type.')
        if self.config.has_key('contentsCss'):
            
            if  isinstance(self.config['contentsCss'], (list, tuple)):
                self.config['contentsCss'] = [settings.STATIC_URL+css for css in self.config['contentsCss']]
            else:
                self.config['contentsCss']=settings.STATIC_URL+self.config['contentsCss']
            
    def render(self, name, value, attrs={}):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        self.config['filebrowserUploadUrl'] = reverse('ckeditor_upload')
        self.config['filebrowserBrowseUrl'] = reverse('ckeditor_browse')
        return mark_safe(u'''<textarea%(attr)s>%(value)s</textarea>
        <script type="text/javascript">
              
            if(typeof(%(id_s)s_id) === 'undefined') {
                %(id_s)s_id = "%(id)s";
                %(id_s)s_timer = null;
                %(id_s)s_config = %(config)s
            } else if (%(id_s)s_timer !== null) {
                clearTimeout(%(id_s)s_timer);
            }
            
            %(id_s)s_timer = setTimeout( function() {
                if (!CKEDITOR.instances[%(id_s)s_id]) {
                    CKEDITOR.replace(%(id_s)s_id, %(id_s)s_config);
                }
                %(id_s)s_timer = null;
            }, 100);
            
             
             
        </script>''' % {'attr':flatatt(final_attrs), 'value':conditional_escape(force_unicode(value)), 'id':final_attrs['id'], 'id_s' :final_attrs['id'].replace('-','_'), 'config':json_encode(self.config)})
