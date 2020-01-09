'use strict';

/* App Module */

var qcResolver = angular.module('qcResolver', [
  'ngRoute',
  'ngCookies',
  'resolverControllers',
  'resolverFilters',
  'restangular',
  'ui.bootstrap',
]);

qcResolver.config(['$routeProvider', 'RestangularProvider',
  function($routeProvider, RestangularProvider) {
    // $resourceProvider.defaults.stripTrailingSlashes = false;
    // $httpProvider.defaults.headers.post['X-CSRFToken'] = $('input[name=csrfmiddlewaretoken]').val();
      
    RestangularProvider.setRequestSuffix('/');
    RestangularProvider.setBaseUrl('api');
    $routeProvider.
      when('/lots', {
        templateUrl: '/static/qc_resolver/templates/lot_list.html',
        controller: 'LotListCtrl'
      }).
      when('/lots/resolve_lot/:lotPK', {
        templateUrl: '/static/qc_resolver/templates/resolve_lot.html',
        controller: 'LotResolverCtrl'
      }).
      otherwise({
        redirectTo: '/lots'
      });
  }]);

qcResolver.run(['$http', '$cookies',
  function($http, $cookies){
      // $http.defaults.headers.post['X-CSRFToken'] = $('input[name=csrfmiddlewaretoken]').val();//$cookies.csrftoken;
      $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;
  }
]);

qcResolver.directive('onRepeatEnd', ['$timeout', function($timeout) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs){
            if(scope.$last == true) {
                $timeout(function () {
                    scope.$emit('ngRepeatFinished');
                });
            }
        }  
    };
}]);

//custom status validator.  status is valid if it is in the STATUS_CHOICES list, invalid otherwise
qcResolver.directive('status', ['Restangular', function(Restangular) {
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            // Use an asynchronous validator; need to wait for the query 'constant_query' to finish, use the result of the inner function
            ctrl.$asyncValidators.status = function(modelValue, viewValue) {
                
                return scope.constant_query.then(function(constants){

                    if (!(scope.STATUS_CHOICES.indexOf(viewValue) > -1)) {
                        ctrl.$setValidity('status', false);
                        //return false //this used to work without having to use $setvalidity...
                    }
                    else {
                        ctrl.$setValidity('status', true);
                        //return true
                    }
                });
            };
        }
    };
}]);

qcResolver.directive('resolve', ['Restangular', '$q', function(Restangular, $q) {
    return {
        require: 'ngModel',
        link: function(scope, elm, attrs, ctrl) {
            // Use an asynchronous validator; need to wait for the query 'constant_query' to finish, use the result of the inner function
            ctrl.$asyncValidators.resolve = function(modelValue, viewValue) {
                //unwrap these functions to debug 
                return scope.constant_query.then(function(constants){

                    if (!(scope.RESOLVE_CHOICES.indexOf(viewValue) > -1)) {
                        // console.log('foo');
                        ctrl.$setValidity('status', false);
                    }
                    else {
                        ctrl.$setValidity('status', true);
                    }
                });
            };
            
        }
    };
}]);
















