

/* Companion functions, stolen from Sarissa */

function selectNodes (sExpr, returnSingle) {
    var nsDoc = gm.atom_doc;
    function nsresolver(prefix) {
	return gm.ns[prefix] || null;
    }
    var result = null;
    if(!returnSingle){
        var oResult = nsDoc.evaluate(sExpr,
            nsDoc,
            nsresolver,
            XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        var nodeList = new SarissaNodeList(oResult.snapshotLength);
        nodeList.expr = sExpr;
        for(var i=0;i<nodeList.length;i++){
            nodeList[i] = oResult.snapshotItem(i);
        }
        result = nodeList;
    }
    else {
	var xf = XPathResult.FIRST_ORDERED_NODE_TYPE;
        result = nsDoc.evaluate(sExpr,
			       nsDoc,
			       nsresolver,
			       xf, null).singleNodeValue;
    }
    return result;      
};

function selectSingleNode (sExpr) {
    return selectNodes(sExpr, true);
}
 
function SarissaNodeList (i) {
    this.length = i;
};


