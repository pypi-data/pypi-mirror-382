import { INotebookTracker } from '@jupyterlab/notebook';
import * as packageData from '../package.json';
const notebookState = new WeakMap();
function getGoFigrMessage(panel) {
    return {
        url: document.URL,
        notebook_path: panel.context.path,
        notebook_local_path: panel.context.localPath,
        title: panel.title.label,
        extension_version: packageData.version
    };
}
function sendGoFigrMessage(panel) {
    const state = notebookState.get(panel);
    const msg = getGoFigrMessage(panel);
    if (state && state.comm) {
        state.comm.send(msg);
    }
}
/**
 * Initialization data for the my-extension extension.
 */
const plugin = {
    id: 'gofigr:plugin',
    description: 'A JupyterLab extension that watches for cell execution',
    autoStart: true,
    requires: [INotebookTracker],
    activate: (app, tracker) => {
        console.log('JupyterLab GoFigr extension active');
        // Function to attach cell execution watcher to a notebook panel
        const watchCellExecution = (panel) => {
            // Listen for the executed signal on the notebook content
            if (!notebookState.has(panel)) {
                notebookState.set(panel, {
                    kernel: null,
                    comm: null
                });
            }
            panel.sessionContext.kernelChanged.connect((sender, args) => {
                console.log(`Kernel started/restarted for notebook at path: ${panel.context.path}`);
                const newKernel = args.newValue;
                newKernel === null || newKernel === void 0 ? void 0 : newKernel.registerCommTarget("gofigr", (comm, msg) => {
                    var _a, _b;
                    console.log("Kernel Comm established. Message: ", msg);
                    notebookState.set(panel, {
                        comm: comm,
                        kernel: newKernel
                    });
                    console.log((_b = (_a = notebookState.get(panel)) === null || _a === void 0 ? void 0 : _a.comm) === null || _b === void 0 ? void 0 : _b.commId);
                    sendGoFigrMessage(panel);
                });
            });
            panel.content.stateChanged.connect((sender, args) => {
                sendGoFigrMessage(panel);
            });
        };
        // Apply watcher to all existing notebook panels
        tracker.forEach((panel) => {
            watchCellExecution(panel);
        });
        // Apply watcher to any new notebook panels
        tracker.widgetAdded.connect((sender, panel) => {
            watchCellExecution(panel);
        });
    }
};
export default plugin;
