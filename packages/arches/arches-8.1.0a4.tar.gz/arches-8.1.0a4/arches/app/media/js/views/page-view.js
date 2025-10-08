import $ from 'jquery';
import _ from 'underscore';
import Backbone from 'backbone';
import ko from 'knockout';
import arches from 'arches';
import viewData from 'view-data';
import AlertViewModel from 'viewmodels/alert';
import ProvisionalHistoryList from 'views/provisional-history-list';
import NotificationsList from 'views/notifications-list';
import ariaUtils from 'utils/aria';
import backToTop from 'utils/back-to-top';
import 'bindings/scrollTo';
import 'bootstrap';
import 'bindings/slide';
import 'jquery-ui';


/**
* A backbone view representing a basic page in arches.  It sets up the
* viewModel defaults, optionally accepts additional view model data and
* binds the view model to the entire page.  When using, no other views
* should bind data to the DOM.
*
* @augments Backbone.View
* @constructor
* @name PageView
*/
var PageView = Backbone.View.extend({
    el: $('body'),

    /**
    * Creates an instance of PageView, optionally using a passed in view
    * model
    *
    * @memberof PageView.prototype
    * @param {object} options
    * @param {object} options.viewModel - an optional view model to be
    *                 bound to the page
    * @return {object} an instance of PageView
    */
    constructor: function(options) {
        var self = this;
        this.viewModel = (options && options.viewModel) ? options.viewModel : {};
        this.viewModel.helploaded = ko.observable(false);
        this.viewModel.helploading = ko.observable(false);
        this.viewModel.helpOpen = ko.observable(false);
        this.viewModel.editsOpen = ko.observable(false);
        this.viewModel.notifsOpen = ko.observable(false);
        this.viewModel.provisionalHistoryList = new ProvisionalHistoryList({
            items: ko.observableArray(),
            helploading: this.viewModel.helploading
        });
        this.viewModel.notifsList = new NotificationsList({
            items: ko.observableArray(),
            helploading: this.viewModel.helploading
        });

        _.defaults(this.viewModel, {
            helpTemplate: ko.observable(viewData.help),
            alert: ko.observable(null),
            loading: ko.observable(false),
            showTabs: ko.observable(false),
            tabsActive: ko.observable(false),
            menuActive: ko.observable(false),
            recentsActive: ko.observable(false),
            unreadNotifs: ko.observable(false),
            dirty: ko.observable(false),
            showConfirmNav: ko.observable(false),
            navDestination: ko.observable(''),
            handleEscKey: ariaUtils.handleEscKey,
            shiftFocus: ariaUtils.shiftFocus,
            backToTopHandler: backToTop.backToTopHandler,
            urls: arches.urls,
            navigate: function(url, bypass) {
                if (!bypass && self.viewModel.dirty()) {
                    self.viewModel.navDestination(url);
                    self.viewModel.alert(new AlertViewModel(
                        'ep-alert-blue',
                        arches.translations.confirmNav.title,
                        arches.translations.confirmNav.text,
                        function() {
                            self.viewModel.showConfirmNav(false);
                        }, function() {
                            self.viewModel.navigate(self.viewModel.navDestination(), true);
                        }
                    ));
                    return;
                }
                self.viewModel.alert(null);
                self.viewModel.loading(true);
                window.location.assign(url);
            },
            getHelp: function(template) {
                self.viewModel.helploading(true);
                var el = document.createElement('div');
                $('.ep-help-content').append(el);
                $.ajax({
                    type: "GET",
                    url: arches.urls.help_template,
                    data: {'template': template}
                }).done(function(data) {
                    $(el).html(data);
                    self.viewModel.helploading(false);
                    $(el).find('.ep-help-topic-toggle').click(function() {
                        var sectionEl = $(this).closest('div');
                        var iconEl = $(this).find('i');
                        if (iconEl.hasClass("fa-chevron-right")) {
                            iconEl.removeClass("fa-chevron-right");
                            iconEl.addClass("fa-chevron-down");
                        } else {
                            iconEl.removeClass("fa-chevron-down");
                            iconEl.addClass("fa-chevron-right");
                        }
                        var contentEl = $(sectionEl).find('.ep-help-topic-content').first();
                        let contentExpanded = contentEl.css('display');
                        if (contentExpanded) {
                            if (contentExpanded === 'none') {
                                $(this).attr('aria-expanded', 'true');
                            } else if (contentExpanded === 'block') {
                                $(this).attr('aria-expanded', 'false');
                            }
                        }
                        contentEl.slideToggle();
                    });
                    $(el).find('.reloadable-img').click(function(){
                        $(this).attr('src', $(this).attr('src'));
                    });
                });
            },
            getProvisionalHistory: function() {
                self.viewModel.provisionalHistoryList.updateList();
            },
            getNotifications: function() {
                self.viewModel.notifsList.updateList();
            },
            openNotifs: function(openButton, escListenScope, closeButton) {
                self.viewModel.getNotifications();
                self.viewModel.notifsOpen(!(self.viewModel.notifsOpen()));
                setTimeout(() => {self.viewModel.handleEscKey(openButton, escListenScope, closeButton)}, 500);
            },
            openEdits: function(openButton, escListenScope, closeButton) {
                self.viewModel.getProvisionalHistory();
                self.viewModel.editsOpen(!(self.viewModel.editsOpen()));
                setTimeout(() => {self.viewModel.handleEscKey(openButton, escListenScope, closeButton)}, 500);
            },
            openHelp: function(helpTemplates, openButton, escListenScope, closeButton) {
                helpTemplates.forEach(template => self.viewModel.getHelp(template));
                self.viewModel.helpOpen(!(self.viewModel.helpOpen()));
                setTimeout(() => {self.viewModel.handleEscKey(openButton, escListenScope, closeButton)}, 500);
            },
            closeNotifs: function() {
                self.viewModel.getNotifications();
                self.viewModel.notifsOpen(false);
                self.viewModel.shiftFocus('#ep-notifs-button');
            },
            closeEdits: function() {
                self.viewModel.editsOpen(false);
                self.viewModel.shiftFocus('#ep-edits-button');
            },
            closeHelp: function() {
                let el = $('.ep-help-content');
                el.empty();
                self.viewModel.helpOpen(false);
                self.viewModel.shiftFocus('#ep-help-button');
            },
        });
        self.viewModel.notifsList.items.subscribe(function(list) {
            self.viewModel.unreadNotifs((list.length > 0));
        });

        self.viewModel.translations = arches.translations;

        window.addEventListener('pageshow', function(event) {
            if (event.persisted) {
                // If the page was restored from cache, hide the loading mask
                self.viewModel.loading(false);
            }
        });

        window.addEventListener('beforeunload', function() {
            self.viewModel.loading(true);
        });

        Backbone.View.apply(this, arguments);
        return this;
    },

    initialize: function() {
        ko.applyBindings(this.viewModel);
        this.viewModel.getNotifications();

        $('[data-toggle="tooltip"]').tooltip();

        backToTop.scrollToTopHandler();
    }
});
export default PageView;
