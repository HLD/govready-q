import React, {useState} from 'react';
import { renderInto } from '../shared/render';
import { RequestsTable } from './requests';
import { Provider } from "react-redux";
import store from "../../store";

window.requestsTable = ( elementId, is_owner ) => {
    $(window).on('load', function () {
        $("#content").show();
        renderInto(document.getElementById('requests-table'), (
            <Provider store={store}>
                <RequestsTable elementId={elementId} isOwner={is_owner}/>
            </Provider>
        ));
    });
};