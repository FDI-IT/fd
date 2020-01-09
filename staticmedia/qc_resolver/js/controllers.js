//'use strict';

/* Controllers */

    
var resolverControllers = angular.module('resolverControllers', []);

function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x < y) ? -1 : ((x > y) ? 1 : 0));
    });
}

function formatDate(date) {
    var yyyy = date.getFullYear().toString();
    var mm = (date.getMonth()+1).toString();
    var dd = date.getDate().toString();
    
    // CONVERT mm AND dd INTO chars
    var mmChars = mm.split('');
    var ddChars = dd.split('');
     
    // CONCAT THE STRINGS IN YYYY-MM-DD FORMAT
    var datestring = yyyy + '-' + (mmChars[1]?mm:"0"+mmChars[0]) + '-' + (ddChars[1]?dd:"0"+ddChars[0]);
    return datestring;
}

resolverControllers.controller('LotListCtrl', ['$scope', '$filter', '$timeout', 'Restangular', 
    function($scope, $filter, $timeout, Restangular) {
    
    //Pagination Stuff
    $scope.paginatedLots = [];
    $scope.currentPage = 1;
    $scope.numPerPage = 10;
    $scope.maxSize = 20;
    $scope.itemsPerPage = 10;

    $scope.loading = true;

    //Date Range filter stuff
    $scope.customDate = false; //false when user is selecting from dateRangeOptions
    $scope.currentDate = new Date();
    $scope.endDate = new Date();
    
    $scope.dateRangeOptions = [
        {label:'Last 30 Days', value:new Date(new Date().setDate($scope.endDate.getDate() - 30))},
        {label:'Last 1 Year', value:new Date(new Date().setDate($scope.endDate.getDate() - 365))},
        {label:'Last 2 Years', value:new Date(new Date().setDate($scope.endDate.getDate() - 730))},
        {label:'All Lots', value:new Date("January 1, 2000")},
    ];

    $scope.selectedRange = $scope.dateRangeOptions[1];

    $scope.startDate = $scope.selectedRange.value;

    $scope.updateRange = function() {
        //this function updates the range when the user selects an option from the select field
        //for these options, the end date should always be the current day
        
        //if customDate is not selected and either the start date or end date has changed
        if (($scope.customDate == false) && (($scope.startDate != $scope.selectedRange.value) || ($scope.endDate != $scope.currentDate))) {
            $scope.endDate = $scope.currentDate; //the user may have changed the end date, make sure it's the current day
            $scope.startDate = $scope.selectedRange.value;
            $scope.getLots();
        }
    };
    
    $scope.filtered = null;

    //run this function to retrieve new set of lots with different date range
    $scope.getLots = function() {
        $scope.loading = true;
        Restangular.all('lots').getList({"start_date":formatDate($scope.startDate),"end_date":formatDate($scope.endDate)}).then(function(lots) {
    
            $scope.loading = false;
            $scope.lots = lots;
            $scope.Math = Math;
            
            $scope.totalItems = lots.length;
            $scope.updateNumPages();
            
        });
    };
    
    $scope.getLots();
    

    // Query the API with Restangular to get the QC_CHOICES from the backend
    $scope.constant_query = Restangular.all('constants').getList();
    $scope.constant_query.then(function(constants){
        
        // console.log(constants);
        $scope.QC_CHOICES = constants[0]["QC_CHOICES"];
        
        //$filters contains data on which subfilters are considered resolved/unresolved
        $scope.filters = {};
        //subfilters contains all the status choices and a boolean field indicating whether or not they are checked
        $scope.subfilters = {};
        
        $scope.filters['Resolved'] = {'checked': false, 'expand': false, 'subfilters': $scope.QC_CHOICES['Resolved']};
        for (var i=0; i<$scope.QC_CHOICES['Resolved'].length; i++) {
            $scope.subfilters[$scope.QC_CHOICES['Resolved'][i]] = false;
        }
        $scope.filters['Unresolved'] = {'checked': true, 'expand': false, 'subfilters': $scope.QC_CHOICES['Unresolved']};
        for (var i=0; i<$scope.QC_CHOICES['Unresolved'].length; i++) {
            $scope.subfilters[$scope.QC_CHOICES['Unresolved'][i]] = true;
        }
        
        $scope.isResolved = function(status) {
            return $scope.QC_CHOICES['Resolved'].indexOf(status) > -1;
        };

    });

    // This is what subfilters and filters look like if i hardcoded them
    // $scope.subfilters = {
        // 'Passed': false,
        // 'Rejected': false,
        // 'Expired': false,
        // 'Created': true,
        // 'In Production': true,
        // 'Pending QC': true,
        // 'Hold': true,
        // 'Resample': true,
        // 'Rework': true,
        // 'Duplicate': true,
        // 'Under Review': true,
        // 'Pending': true,
        // 'Not Passed...': true,
        // 'Destroyed': true,
    // };
//    
    // $scope.filters = {
        // 'Resolved': {'checked': false, 'expand': false, 'subfilters': ['Passed','Rejected','Expired']},
        // 'Unresolved': {'checked': true, 'expand': false, 'subfilters':
            // [
                // 'Created',
                // 'In Production',
                // 'Pending QC',
                // 'Hold',
                // 'Resample',
                // 'Rework',
                // 'Duplicate',
                // 'Under Review',
                // 'Pending',
                // 'Not Passed...',
                // 'Destroyed',
            // ]}
    // };
//     

    //run this function when the expand/collapse button is clicked
    $scope.toggleExpand = function(filter_group_name) {
        $scope.filters[filter_group_name].expand = !$scope.filters[filter_group_name].expand;
    };
    
    //function used to filter lots using the checked subfilters.  if no filters are selected, all lots are displayed
    $scope.filterByStatus = function (lot) {
        return $scope.subfilters[lot.status] || noFilter($scope.subfilters);
    };
    
    //complex filter is on by default
    $scope.complexFilter = true;
    
    $scope.filterComplexLots = function(lot) {
        //if the complex filter is checked, display a lot only if it is complex
        //if the complex filter is unchecked, display all lots. (!$scope.complexFilter wil return true)  
        return ($scope.complexFilter && isComplexLot(lot)) || !$scope.complexFilter;
    };
    
    function isComplexLot(lot) {
        var testcard_count = 0;
        for (i=0;i<lot.retains.length;i++) {
            testcard_count = testcard_count + lot.retains[i].testcards.length;
        }
        if (testcard_count > 1) {
            return true;
        }        
        else {
            return  false;
        }
    }
    
    //returns true if no filters are selected...
    function noFilter(filterObj) {
        for (var key in filterObj) {
            if (filterObj[key]) {
                return false;
            }
        }
        return true;
    }
    
    //selects/unselects all subfilters when a user checks/unchecks a filter group
    $scope.selectAllSubfilters = function(filter_group_name) { 
        var filter_group_data = $scope.filters[filter_group_name];
        
        for (var i=0; i<filter_group_data.subfilters.length; i++) {
            $scope.subfilters[filter_group_data.subfilters[i]] = filter_group_data.checked;
        }
    };

    //'ngRepeatFinished' is emmited by the 'OnRepeatEnd' directive when an ng-repeat loop ends.
    // This is used to update the number of pages (for pagination) each time the lots are filtered
    $scope.$on('ngRepeatFinished', function(ngRepeatFinishedEvent){
       $scope.updateNumPages();
    });

    $scope.updateNumPages = function() {
        $timeout(function() {
            //wait for 'filtered' to be changed
            //number of pages is NO LONGER defined by 'num-pages', now defined by 'total-items' and 'items-per-page'
           $scope.totalItems = $scope.filtered.length;
        }, 10);
    };
    

}]);



/* LOT RESOLVER CONTROLLER */
resolverControllers.controller('LotResolverCtrl', ['$scope', '$modal', '$routeParams', 'Restangular', function($scope, $modal, $routeParams, Restangular) {
    
    //Restangular query to get the single lot
    Restangular.one('lots', $routeParams.lotPK).get().then(function(lot) {
        
        //sort the lot's retains by retain number (is higher number always later?)
        sortByKey(lot.retains, 'retain');
        
        //for each retain, sort its testcards by qc_time/scan_time
        for (i=0;i<lot.retains.length;i++) {
            
            //i create a temporary key called 'sort_time' that contains the time we will sort the testcards by 
            //this way i dont have to change the sort function to use another key if the first key is null
            for (k=0;k<lot.retains[i].testcards.length;k++){
                var tc = lot.retains[i].testcards[k];
                tc.qc_time === null ? tc['sort_time'] = tc.scan_time : tc['sort_time'] = tc.qc_time;
            }
            sortByKey(lot.retains[i].testcards, 'sort_time');
            // lot.retains[i].testcards.sort(function(a, b) {
                // //if there is a qc time, use it to order the testcards.  otherwise, use scan time 
                // return parseFloat(a.qc_time === null ? a.scan_time : a.qc_time) - parseFloat(b.qc_time === null ? b.scan_time : b.qc_time); 
             // });
        }
        
        //set scope variables.  stored_lot is used to determine if any changes were made 
        $scope.lot = lot;
        $scope.stored_lot = angular.copy(lot);  

        // first_retain = $scope.lot.retains[0]
        $scope.currentTestcard = $scope.lot.retains[0].testcards[0];
        // $scope.currentTestcard = sortByKey(first_retain.testcards, 'scan_time')[0];
        
        var retain_notes = new Array();
        for(var i=0; i<lot.retains.length; i++) {
            retain_notes[lot.retains[i].id] = {"concatenated_testcards": "", "additional": ""};
        }
        $scope.retain_notes = retain_notes;
    
        Restangular.all('nextLot').getList({"current_lot_pk":$scope.lot.id}).then(function(nextLot){
           $scope.nextLotId = nextLot[0];   
        });
        
    });
    
    //Put this query in the scope because it needs to be used by the status validator directive
    $scope.constant_query = Restangular.all('constants').getList();
    
    //After the request has returned a response, STATUS_CHOICES is defined (this is asynchronous)
    $scope.constant_query.then(function(constants){
        $scope.STATUS_CHOICES = constants[0]["STATUS_CHOICES"];
        $scope.RESOLVE_CHOICES = constants[0]["QC_CHOICES"]["Resolved"];
    });
    
   
    //keeps track of whether the user has clicked 'submit'
    $scope.submitted = false;      

    $scope.setTestcard = function(testcard) {
      $scope.currentTestcard = testcard;
    };

    //not currently used, concatenates a retain's testcard notes
    $scope.updateNotes = function(retain) {
        if(retain.concatenate_notes) {
            var testcard_notes = new Array();
                        
            for(var i=0; i<retain.testcards.length; i++) {
                if(typeof retain.testcards[i].notes == "string" && retain.testcards[i].notes != '') {
                    testcard_notes.push(retain.testcards[i].notes);
                }
                // text = text + (typeof retain.testcards[i].notes == "string" ? retain.testcards[i].notes : '') + (i==retain.testcards.length-1 ? '' : ',');
            }
            
            retain.notes = testcard_notes.join(", ");
        }
    };
          
    $scope.getNextLotId = function() {

        Restangular.all('nextLot').getList().then(function(nextLot){
           $scope.nextLotId = nextLot[0];   
        });
    };
          
    // $scope.postLot = function(lot) {
//         
        // //I get an error when I try to post the image fields (even though I don't change them)
        // //To work around this, I just get delete them from the lot, and use PATCH (rather than POST),
        // // which updates the fields that I supply, and keeps any other fields (these image fields) unchanged
        // for(var i=0; i<lot.retains.length; i++){
            // for(var k=0; k<lot.retains[i].testcards.length; k++) {
                // current_testcard = lot.retains[i].testcards[k];
                // delete current_testcard["large"];
                // delete current_testcard["thumbnail"];
                // delete current_testcard["sort_time"];
            // }
        // }
//         
        // lot.patch().then(function(lot) {
            // console.log("Post successful");
//             
            // if ($scope.nextLot) {
                // // $scope.getNextLotId();
                // console.log("waiting for query...");
                // $scope.$watch("nextLotId", function() {
                    // console.log($scope.nextLotId);
                    // window.location.replace('/qc/qc_resolver/#/lots/resolve_lot/' + $scope.nextLotId);  
                // });
            // }
            // else {
                // window.location.replace('/qc/qc_resolver/#/lots');
            // }
        // }, function() {
            // window.alert("Could not post data to the database.  Check the console for errors.");
            // console.log("There was an error posting");
        // });  
    // };
    
    // Warn the user if they try to leave the page without saving
    function closeEditorWarning(){
        return 'If you leave before submitting your changes will be lost.';
    }
    
    window.onbeforeunload = closeEditorWarning;
   
    $scope.validate = function() {
        if ($scope.resolveForm.$invalid) {
            window.alert('Fix the error(s) in the red panels.');
        }
        else if (angular.equals($scope.stored_lot, $scope.lot)) {
            window.alert('No changes have been made.');
        }
        else {
            $scope.openModal();
        }
    };
    
    /* Modal Stuff */
    $scope.openModal = function() {
        
        var modalInstance = $modal.open({
            templateUrl: '/static/qc_resolver/templates/resolveSummary.html',
            controller: 'resolveSummaryCtrl',
            resolve: {
                old_lot: function() {
                    return $scope.stored_lot;
                },
                new_lot: function() {
                    return $scope.lot;
                },
                nextLotId: function() {
                    return $scope.nextLotId;
                }
            },
            size: 'md'
        });
       
        modalInstance.result.then(function(nextLot) {
           // if this block is reached, it means the user clicked 'Save Changes' ($modal.close(result))
           $scope.nextLot = nextLot;
           // $scope.postLot($scope.lot);
        }, function() {
           // if this block is reached, the user closed the modal without saving ($modal.dismiss)
           console.log('Modal dismissed');
        });
    };
       
}]);


//controller for the resolve summary modal
resolverControllers.controller('resolveSummaryCtrl', ['$scope', '$modalInstance', 'old_lot', 'new_lot', 'nextLotId', function($scope, $modalInstance, old_lot, new_lot, nextLotId) {
    $scope.old_lot = old_lot;
    $scope.new_lot = new_lot;
    $scope.nextLotId = nextLotId;
    $scope.nextLot = true;
    
    $scope.show_changes = true;
    $scope.saving = false;
   
    // $scope.save = function() {
        // $modalInstance.close($scope.nextLot);
    // };
    
    $scope.postLot = function(lot) {
        
        //I get an error when I try to post the image fields (even though I don't change them)
        //To work around this, I just get delete them from the lot, and use PATCH (rather than POST),
        // which updates the fields that I supply, and keeps any other fields (these image fields) unchanged
        for(var i=0; i<lot.retains.length; i++){
            for(var k=0; k<lot.retains[i].testcards.length; k++) {
                current_testcard = lot.retains[i].testcards[k];
                delete current_testcard["large"];
                delete current_testcard["thumbnail"];
                delete current_testcard["sort_time"];
            }
        }
        
        lot.patch().then(function(lot) {
            console.log("Post successful");
            
            if ($scope.nextLot) {
                // $scope.getNextLotId();
                console.log("waiting for query...");
                $scope.$watch("nextLot", function() {
                    console.log($scope.nextLotId);
                    window.location.replace('/qc/qc_resolver/#/lots/resolve_lot/' + $scope.nextLotId);  
                });
                $modalInstance.close($scope.nextLot);
            }
            else {
                window.location.replace('/qc/qc_resolver/#/lots');
                $modalInstance.close($scope.nextLot);
            }
        }, function() {
            window.alert("Could not post data to the database.  Check the console for errors.");
            console.log("There was an error posting");
        });  
    };
    
    
    //TODO show the user that the lot is being saved
    $scope.save = function() {
        $scope.saving = true;
        $scope.postLot($scope.new_lot);
    };
    
    $scope.cancel = function() {
        $modalInstance.dismiss('cancel');
    };
    
    $scope.getOldRetain = function(new_retain) {
        for(var i=0; i<old_lot.retains.length; i++) {
            if (old_lot.retains[i].retain == new_retain.retain) {
                return old_lot.retains[i];
            }
        }
    };
    
    $scope.getOldTestcard = function(new_retain, new_testcard) {
        for(var i=0; i<old_lot.retains.length; i++) {
            if (old_lot.retains[i].retain == new_retain.retain) {
                for(var k=0; k<old_lot.retains[i].testcards.length; k++) {
                    if (old_lot.retains[i].testcards[k].id == new_testcard.id){
                        return old_lot.retains[i].testcards[k];
                    }
                }
            }
        }
    };
      
}]);



