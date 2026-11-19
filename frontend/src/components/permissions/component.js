import React, {useState} from 'react';
import { renderInto } from '../shared/render';
import { Permissions } from './permissions';
import { Provider } from "react-redux";
import store from "../../store";

window.permissionsTable = ( elementId, is_owner ) => {
  
    $(window).on('load', function () {
        $("#content").show();
        renderInto(document.getElementById('perm-table'), (
            <Provider store={store}>
                <Permissions elementId={elementId} isOwner={is_owner} />
            </Provider>
        ));
    });
};
