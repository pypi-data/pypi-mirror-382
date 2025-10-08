import ko from 'knockout';
import WidgetViewModel from 'viewmodels/widget';
import urlDatatypeWidgetTemplate from 'templates/views/components/widgets/urldatatype.htm';


var name = 'urldatatype';
const viewModel = function(params) {
    const self = this;
    params.configKeys = ['url_placeholder','url_label_placeholder','link_color'];
    params.valueProperties = ['url', 'url_label'];

    WidgetViewModel.apply(this, [params]);

    if (ko.isObservable(this.value)) {
    
        // #10027 assign this.url & this.url_label with value versions for updating UI with edits
        if (this.value()) {
            var valueUrl = this.value().url;
            var valueUrlLabel = this.value().url_label;
            this.url(valueUrl);
            this.url_label(valueUrlLabel);
        }

        this.value.subscribe(function(newValue) {
            if (newValue) {
                if (newValue.url) {
                    self.url(newValue.url);
                } else {
                    self.url(null);
                }
                if (newValue.url_label) {
                    self.url_label(newValue.url_label);
                } else {
                    self.url_label(null);
                    newValue.url_label = null;
                }
            } else {
                self.url(null);
                self.url_label(null);
                newValue.url = null;
                newValue.url_label = null;
            }
        });

    } else {
        if (this.value) {
            this.value.url.subscribe(function(newUrl) {
                if (newUrl) {
                    self.url(newUrl);
                } else {
                    self.url(null);
                }
            })
            this.value.url_label.subscribe(function(newUrlLabel) {
                if (newUrlLabel) {
                    self.url_label(newUrlLabel);
                } else {
                    self.url_label(null);
                }
            })
        }
    }

    this.urlPreviewText = ko.pureComputed(function() {
        if(self.url()){
            if (self.url_label && self.url_label()) {
                return self.url_label();
            } else if (self.url && self.url()) {
                return self.url();
            }
        }
        else{
            return "--";
        }
    }, this);
    
};

ko.components.register(name, {
    viewModel: viewModel,
    template: urlDatatypeWidgetTemplate,
});

export default name;
