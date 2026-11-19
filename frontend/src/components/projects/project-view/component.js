import React from 'react';
import { renderInto } from '../../shared/render';
import { projectTagsStateSlice } from "./slice"
import { Provider } from "react-redux";
import store from "../../../store";
import {TagDropdown} from "../../shared/tag-dropdown";


const { setTags } = projectTagsStateSlice.actions;

window.renderProjectTags = (projectID, existingTags) => {
    store.dispatch(setTags(existingTags));

    $(window).on('load', function () {
        $("#content").show();
    });

    renderInto(document.getElementById('show-tags'), (
        <Provider store={store}>
            <TagDropdown
                action={setTags}
                updateTagsURL={`/api/v2/projects/${projectID}/tags/`}
                existingTags={existingTags} />
        </Provider>
    ));

};
