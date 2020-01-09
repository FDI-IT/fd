'use strict';

describe('QC Resolver Controllers', function() {
    
    beforeEach(angular.mock.module('qcResolver'));
    // beforeEach(angular.mock.module('resolverControllers'));

    describe('LotListCtrl', function() {

        var scope, ctrl, Restangular, httpBackend;
        console.log('This gets logged successfully...');
        
        beforeEach(angular.mock.inject(['$rootScope', '$controller', 'Restangular', '$httpBackend',
        function($rootScope, $controller, _Restangular_, $httpBackend) {
            scope = $rootScope.$new();
            ctrl = $controller('LotListCtrl', {$scope: scope});
            Restangular = _Restangular_;
            httpBackend = $httpBackend;
            httpBackend.expectGET("http://localhost/qc/api/lots/?end_date=2014-12-03&start_date=2013-12-03").respond([{'foo':'bar'}]);
        }]));
        
        it('check that test function works correctly', function() {
            console.log('in test');
            expect(scope.testFunction('foo')).toEqual(true);
        });
        
        it('check that get constants query returns the correct functions/variables', function() {
            httpBackend.expectGET("http://localhost/qc/api/constants/").respond([{'foo':'bar'}]);
            var constant_query = scope.constant_query;
            constant_query.then(function(constants) {
                expect(scope.isResolved('Passed')).toEqual(true);
                expect(scope.isResolved('Expired')).toEqual(true);
                expect(scope.isResolved('Hold')).toEqual(false);                
            });
            httpBackend.flush();
        });

    });
});

// describe('Test to print out jasmine version', function() {
// it('prints jasmine version', function() {
        // console.log('jasmine-version:' + jasmine.getEnv().versionString());
    // });
// });