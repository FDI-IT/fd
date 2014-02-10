import collections

from django.utils import simplejson

from access import models


Node = collections.namedtuple("Node",["ft","js"])

def formulatree_to_jsinfovis(formulatree_mptt_qs):
    nodes = []
    for ft_node in formulatree_mptt_qs:
        nodes.append(Node(
            ft_node,          
            {
                'id':ft_node.lft,
                'name':   ft_node.node_label,
                'data':{'ingredient_info':ft_node.node_ingredient.info_slice,
                        'ingredient_link':ft_node.node_ingredient.url,},
                'children':[],
            }))
        
    nodes_last_parent = [nodes[0],]
    max_depth = 1
    
    for i in range(1,len(nodes)):
        my_node = nodes[i]
        
        if my_node.ft.lft > nodes_last_parent[-1].ft.rgt:
            nodes_last_parent.pop()
        nodes_last_parent[-1].js['children'].append(my_node.js)
        
        if my_node.ft.lft+1 != my_node.ft.rgt:
            nodes_last_parent.append(my_node)
            if len(nodes_last_parent) > max_depth:
                max_depth += 1
            
    return {
        'st_data' : simplejson.dumps(nodes[0].js),
        'max_depth' : max_depth,
    }
    #return HttpResponse(simplejson.dumps({'lot_number':get_next_lot_number()}), content_type='application/json; charset=utf-8')