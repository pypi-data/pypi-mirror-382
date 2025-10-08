import $ from 'jquery';
import ko from 'knockout';
import _ from 'underscore';
import 'datatables.net-buttons-bs';
import 'datatables.net-responsive-bs';
import 'datatables.net-buttons-print';
import 'datatables.net-buttons-html5';

ko.bindingHandlers.datatable = {
    init: function (element, valueAccessor) {
        var config = ko.unwrap(valueAccessor());
        var table = $(element).DataTable(config);
        if (config.columnVis) {
            _.each(config.columnVis, function (vis, i) {
                vis.subscribe(function (val) {
                    var column = table.column(i);
                    column.visible(val);
                });
            });
        }
    }
};
ko.bindingHandlers.datatable.init = ko.bindingHandlers.datatable.init.bind(ko.bindingHandlers.datatable);


ko.bindingHandlers.dataTablesForEach = {
    page: 0,
    init: function (element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
        const options = ko.unwrap(valueAccessor());
        ko.unwrap(options.data);
        if (options.dataTableOptions.serverSide === true) {
            const table = $(element).closest('table').DataTable(options.dataTableOptions);
            table.destroy();
        }
        else {
            if (options.dataTableOptions.paging) {
                valueAccessor().data.subscribe(function (changes) {
                    const table = $(element).closest('table').DataTable();
                    ko.bindingHandlers.dataTablesForEach.page = table.page();
                    table.destroy();
                }, null, 'arrayChange');
            }
            const nodes = Array.prototype.slice.call(element.childNodes, 0);
            ko.utils.arrayForEach(nodes, function (node) {
                if (node && node.nodeType !== 1) {
                    node.parentNode.removeChild(node);
                }
            });
        }
        return ko.bindingHandlers.foreach.init(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext);
    },
    update: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
        const options = ko.unwrap(valueAccessor()),
            key = 'DataTablesForEach_Initialized';
        ko.unwrap(options.data);
        var table;
        if (!options.dataTableOptions.paging) {
            table = $(element).closest('table').DataTable();
            table.destroy();
        }
        ko.bindingHandlers.foreach.update(element, valueAccessor, allBindings, viewModel, bindingContext);
        table = $(element).closest('table').DataTable(options.dataTableOptions);
        if (options.dataTableOptions.paging) {
            if (table.page.info().pages - ko.bindingHandlers.dataTablesForEach.page == 0)
                table.page(--ko.bindingHandlers.dataTablesForEach.page).draw(false);
            else
                table.page(ko.bindingHandlers.dataTablesForEach.page).draw(false);
        }
        if (!ko.utils.domData.get(element, key) && (options.data || options.length))
            ko.utils.domData.set(element, key, true);
        return {
            controlsDescendantBindings: true
        };
    }
};
ko.bindingHandlers.dataTablesForEach.init = ko.bindingHandlers.dataTablesForEach.init.bind(ko.bindingHandlers.dataTablesForEach);
ko.bindingHandlers.dataTablesForEach.update = ko.bindingHandlers.dataTablesForEach.update.bind(ko.bindingHandlers.dataTablesForEach);


export default ko.bindingHandlers.datatable;
