import React, {useState} from 'react';
import { renderInto } from '../shared/render';
import { ComponentParties } from './cmpt_parties';
import { Provider } from "react-redux";
import store from "../../store";

window.cmptPartiesTable = ( elementId, poc_users, is_owner, is_admin ) => {
    $(window).on('load', function () {
        $("#content").show();
        renderInto(document.getElementById('cmpt-parties-table'), (
            <Provider store={store}>
                <ComponentParties elementId={elementId} poc_users={poc_users} isOwner={is_owner} isAdmin={is_admin} />
            </Provider>
        ));
    });
};