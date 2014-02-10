var labelType, useGradients, naiveTextSupport, animate;

(function() {
  var ua = navigator.userAgent,
      iStuff = ua.match(/iPhone/i) || ua.match(/iPad/i),
      typeOfCanvas = typeof HTMLCanvasElement,
      nativeCanvasSupport = (typeOfCanvas == 'object' || typeOfCanvas == 'function'),
      textSupport = nativeCanvasSupport 
        && (typeof document.createElement('canvas').getContext('2d').fillText == 'function');
  //I'm setting this based on the fact that ExCanvas provides text support for IE
  //and that as of today iPhone/iPad current text support is lame
  labelType = (!nativeCanvasSupport || (textSupport && !iStuff))? 'Native' : 'HTML';
  nativeTextSupport = labelType == 'Native';
  useGradients = nativeCanvasSupport;
  animate = !(iStuff || !nativeCanvasSupport);
})();

var Log = {
  elem: false,
  write: function(text){
    if (!this.elem) 
      this.elem = document.getElementById('log');
    this.elem.innerHTML = text;
    this.elem.style.left = (500 - this.elem.offsetWidth / 2) + 'px';
  }
};
var st;
var getTree = (function() {
          return 
   });
   
var refresh_node_details = function(node) {
	var transform={
		'tag':'li',
		'html':'${a} - ${b}'
	};
	var ii = node.data.ingredient_info;
	var count  = 0;
	node.eachSubnode(function(n) { count++; });
	var source_data = [
		{
			'a':'Direct ingredients',
			'b':count
		}
	];
	for (var my_key in ii) {
		if (ii.hasOwnProperty(my_key)) {
			source_data.push({
			    'a':my_key,
			    'b':ii[my_key]
			});
		}
	}
	var node_info_title = '<a href="' + node.data.ingredient_link + '">' + node.name + '</a>'
	jQuery("#node_info").empty().append(node_info_title).json2html(source_data, transform);
};

function init(){
    //init data
   
    //end
    //init Spacetree
    //Create a new ST instance
    st = new $jit.ST({
    	orientation:st_layout_parameters.orientation,
        //id of viz container element
        injectInto: 'infovis',
        constrained:st_layout_parameters.constrained,
        //set duration for the animation
        duration: 800,
        //set animation transition type
        transition: $jit.Trans.Quart.easeInOut,
        //set distance between node and its children
        levelDistance: st_layout_parameters.level_distance,
        levelsToShow: st_layout_parameters.levels_to_show,  
        //enable panning
        Navigation: {
          enable:true,
          panning:true,
          zooming:20
        },
        //set node and edge styles
        //set overridable=true for styling individual
        //nodes or edges
        Node: {
            height: st_layout_parameters.node_height,
            width: st_layout_parameters.node_width,
            type: 'rectangle',
            color: '#aaa',
            overridable: true
        },
        
        Edge: {
            type: 'bezier',
            overridable: true
        },
        
        Events: {
        	enable: true,
        	enableForEdges: false,  
			type: 'auto',  
			onClick: function(node, eventInfo, e) {  
		        refresh_node_details(node); 
		    } 
        },
        
        Tips: {
        	enable: true,
        	onShow: function(tip, node) {
        		tip.innerHTML = node.name;
        	}
        },
        
        request: function(nodeId, level, onComplete) {
        	var ans = getTree(nodeId, level);
        	onComplete.onComplete(nodeId, ans);
        },
        
        onBeforeCompute: function(node){
            Log.write("loading " + node.name);
        },
        
        onAfterCompute: function(){
            Log.write("done");
        },
        
        //This method is called on DOM label creation.
        //Use this method to add event handlers and styles to
        //your node.
        onCreateLabel: function(label, node){
            label.id = node.id;            
            label.innerHTML = node.name;
            label.onclick = function(){
            	 st.onClick(node.id);
            };
            //set label styles
            var style = label.style;
            style.width = st_layout_parameters.node_width + 'px';
            style.height = st_layout_parameters.node_height-3 + 'px';            
            style.cursor = 'pointer';
            style.color = '#333';
            style.fontSize = '0.8em';
            style.textAlign= 'center';
            style.paddingTop = '3px';
        },
        
        //This method is called right before plotting
        //a node. It's useful for changing an individual node
        //style properties before plotting it.
        //The data properties prefixed with a dollar
        //sign will override the global node style properties.
        onBeforePlotNode: function(node){
            //add some color to the nodes in the path between the
            //root node and the selected node.
            if (node.selected) {
                //node.data.$color = "#ff7";
            }
            else {
                delete node.data.$color;
                //if the node belongs to the last plotted level
                if(!node.anySubnode("exist")) {
                    //count children number
                    var count = 0;
                    node.eachSubnode(function(n) { count++; });
                    //assign a node color based on
                    //how many children it has
                    if (count == 0) {
                    	node.data.$color = "#99b";
                    } else if (count > 16) {
                    	node.data.$color = '#ffa';
                    } else {
                    	count = Math.round(count/3);
                    	node.data.$color = ['#8c8', '#9d9', '#aea', '#bea', '#cea', '#cfa'][count];
                    }               
                }
            }
        },
        
        //This method is called right before plotting
        //an edge. It's useful for changing an individual edge
        //style properties before plotting it.
        //Edge data proprties prefixed with a dollar sign will
        //override the Edge global style properties.
        onBeforePlotLine: function(adj){
            if (adj.nodeFrom.selected && adj.nodeTo.selected) {
                adj.data.$color = "#eed";
                adj.data.$lineWidth = 3;
            }
            else {
                delete adj.data.$color;
                delete adj.data.$lineWidth;
            }
        }
    });
    //load json data
    st.loadJSON(st_data);
    //compute node positions and layout
    st.compute();
    //optional: make a translation of the tree
    st.geom.translate(new $jit.Complex(-200, 0), "current");
    //emulate a click on the root node.
    st.onClick(st.root);
    //end
    //Add event handlers to switch spacetree orientation.
    // var top = $jit.id('r-top'), 
        // left = $jit.id('r-left'), 
        // bottom = $jit.id('r-bottom'), 
        // right = $jit.id('r-right'),
        // normal = $jit.id('s-normal');
//         
//     
    // function changeHandler() {
        // if(this.checked) {
            // top.disabled = bottom.disabled = right.disabled = left.disabled = true;
            // st.switchPosition(this.value, "animate", {
                // onComplete: function(){
                    // top.disabled = bottom.disabled = right.disabled = left.disabled = false;
                // }
            // });
        // }
    // };
    
    // top.onchange = left.onchange = bottom.onchange = right.onchange = changeHandler;
    //end

}