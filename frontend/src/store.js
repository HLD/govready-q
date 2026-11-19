import { configureStore } from "@reduxjs/toolkit";

import {componentTagsStateSlice} from "./components/elements/element-detail-tabs/slice"
import {projectTagsStateSlice} from "./components/projects/project-view/slice";
import modalReducer from "./components/shared/modalSlice";

const store = configureStore({
    reducer: {
        componentTags: componentTagsStateSlice.reducer,
        projectTags: projectTagsStateSlice.reducer,
        modal: modalReducer
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware(
        /*YOUR CUSTOM MIDDLEWARES HERE (use .concat())*/
    ),
});

export default store;
window.store = store;
