var gm;

function GuiModel (tree_id, atom_url) {
    this.tree_id = tree_id;
    this.atom_url = atom_url;
    this.tree = document.getElementById(tree_id);
    this.viewer = document.getElementById("selected-entry");
    this.processor = null;
    this.viewerprocessor = null;
    this.atom_doc = null;
    this.curr_tree_selection = 0;
    this.ns = {
	'xhtml' : 'http://www.w3.org/1999/xhtml',
	'mathml': 'http://www.w3.org/1998/Math/MathML',
	'atom'  : 'http://www.w3.org/2005/Atom',
    };

    // Register handlers
    this.tree.addEventListener("click", this.selectEntry, false);
}


GuiModel.prototype.tostring = function (node) {
    /* Dump a document or node to a string representation */

    var s = new XMLSerializer();
    return s.serializeToString(node);
}


GuiModel.prototype.loadURL = function (url) {
    /* Synchronously load some XML, return the document element */

    var xmlhttp = new XMLHttpRequest();  
    xmlhttp.open("GET", url, false);  
    xmlhttp.setRequestHeader("Cache-Control","no-cache");
    xmlhttp.send('');
    return xmlhttp.responseXML;
}


GuiModel.prototype.loadProcessor = function (xslurl) {
    /* Load the XSLT that massages Atom-data into XML datasources */

    this.xsldoc = this.loadURL(xslurl);
    this.processor = new XSLTProcessor();
    this.processor.importStylesheet(this.xsldoc);
}


GuiModel.prototype.loadViewerProcessor = function (xslurl) {
    /* Load the XSLT that views selected entries */

    this.viewerxsldoc = this.loadURL(xslurl);
    this.viewerprocessor = new XSLTProcessor();
    this.viewerprocessor.importStylesheet(this.viewerxsldoc);
}


GuiModel.prototype.reloadModel = function () {
    /* Fetch the atom data, then update various trees */

    Sarissa.updateContentFromURI(gm.atom_url, gm.tree, gm.processor);

}


GuiModel.prototype.selectEntry = function (e) {
    /* Activate the right-hand side */

    e.preventDefault();
    var entrynode = e.target;
    var entryid = entrynode.getAttribute("href");

    // Change the contents of the viewer
    gm.atom_doc.documentElement.setAttribute("selected", entryid);
    var result = gm.viewerprocessor.transformToDocument(gm.atom_doc);
    var iresult = document.importNode(result.documentElement, true);
    Sarissa.moveChildNodes(iresult, gm.viewer); 

}


function initGuiModel () {
    /* Run on document load by the onload handler */

    if (window.location.host.indexOf(":") == -1){
	// Running from FS, not dynamicall via WSGI, use dummy data
	var atom_url = "samplefeed.xml";
    } else {
	var atom_url = "../feed.xml";
    }
    gm = new GuiModel("logtree", atom_url);
    gm.loadProcessor("debugui-html.xsl");
    gm.loadViewerProcessor("debugui-entryviewer.xsl");
    gm.atom_doc = gm.loadURL(atom_url);
    gm.reloadModel();
    console.log("init ran, model loaded");
}
