import React from 'react';
import { renderInto } from '../../shared/render';
import { componentTagsStateSlice } from "./slice"
import { Provider } from "react-redux";
import store from "../../../store";
import { TagDropdown } from "../../shared/tag-dropdown";


const { setTags } = componentTagsStateSlice.actions;

window.renderElementTags = (elementID, existingTags) => {
    store.dispatch(setTags(existingTags));

    $(window).on('load', function () {
        $("#content").show();
    });

    renderInto(document.getElementById('show-tags'), (
        <Provider store={store}>
            <TagDropdown
                action={setTags}
                updateTagsURL={`/api/v2/elements/${elementID}/tags/`}
                existingTags={existingTags} />
        </Provider>
    ));
};
