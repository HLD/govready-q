import React, {useState} from 'react';
import { renderInto } from '../shared/render';
import { SystemSummary } from './system_summary';
import { SystemSummarySpreadsheet } from './system_summary_spreadsheet';
import { Provider } from "react-redux";
import store from "../../store";

window.system_summary = ( systemId, projectId ) => {
    renderInto(document.getElementById('system-summary-poam-datagrid'), (
        <Provider store={store}>
            <SystemSummary systemId={systemId} projectId={projectId} />
        </Provider>
    ));
};

window.system_summary_spreadsheet = ( systemId, projectId ) => {
    renderInto(document.getElementById('system-summary-poam-spreadsheet-datagrid'), (
        <Provider store={store}>
            <SystemSummarySpreadsheet systemId={systemId} projectId={projectId} />
        </Provider>
    ));
};