'use strict';

/* http://docs.angularjs.org/guide/dev_guide.e2e-testing */

describe('qcResolver App', function() {

    // add this back later, commented it out to speed up the test
    it('should redirect qc_resolver to qc_resolver/#/lots', function() {
      browser.get('qc/qc_resolver');
      browser.getLocationAbsUrl().then(function(url) {
          expect(url.split('#')[1]).toBe('/lots');
        });
    });

    

    var flow = protractor.promise.controlFlow();

    describe('Lot List View', function() {
                        
        flow.execute(function() { //if i put an 'it' block here (like i do below), tests fail.   WHY???!?!?
            browser.get('qc/qc_resolver/#/lots');
        });

        var lotList = element.all(by.repeater("lot in filtered = (lots | filter:search | filter:filterByStatus | filter:filterComplexLots)"));
        var ORIGINAL_LOT_COUNT;
        
        flow.execute(function() {
            lotList.count().then(function(count) {
               ORIGINAL_LOT_COUNT = count;
            });
        });
        
        it('filter lots using the search box', function() {        
            flow.execute(function() {
                // expect(ORIGINAL_LOT_COUNT).toBe(5);
                console.log('Original lot count - complex and unresolved only: ' + ORIGINAL_LOT_COUNT);
                
                var search = element(by.model('search'));
     
                search.sendKeys('foobar');
                      
                lotList.count().then(function(count){
                    console.log("Searching 'foobar'... Count: " + count);
                    expect(count).toBeLessThan(ORIGINAL_LOT_COUNT);
                   
                    search.clear();
                });
            });
        });
        
        it('filter lots using resolved/complex checkboxes', function() {
            flow.execute(function() {
                var count_after_checking_resolved;
                var count_after_unchecking_complex;
                var resolved = element(by.css(".Resolved"));
                resolved.click();
                           
                element(by.css(".result-count")).getAttribute('value').then(function(count) {
                    count_after_checking_resolved = count;
                    console.log('Add resolved lots...  Count: ' + count_after_checking_resolved);
                    expect(count_after_checking_resolved >= ORIGINAL_LOT_COUNT).toBeTruthy;
                });

                var complex = element(by.css(".Complex"));
                complex.click(); //uncheck 'Complex' filter
                                
                element(by.css(".result-count")).getAttribute('value').then(function(count) {
                    count_after_unchecking_complex = count;
                    console.log('Add simple lots... Count: ' + count_after_unchecking_complex);
                    expect(count_after_unchecking_complex >= count_after_checking_resolved).toBeTruthy; 
                });

            });
        });
    });


    describe('Lot Resolver View', function() {

        it('test the resolve lot view', function() { //this 'it' block is necessary, without it, the browser redirects too early
            flow.execute(function() {
                browser.get('qc/qc_resolver/#/lots/resolve_lot/50345');
            });
        });
        
        it('try submitting without changing anything', function() {
           var submit_button = element(by.css(".submit-button"));
           submit_button.click();
           
           var alert = browser.switchTo().alert();
           expect(alert.getText()).toEqual("No changes have been made.");
           alert.dismiss();
        });
        
        it('try submitting a non-resolved lot', function() {
           element(by.css('.lot-status')).element(by.cssContainingText('option', 'Hold')).click();
           var lot_error = element(by.css('.lot_error'));
           expect(lot_error.getText()).toEqual("To resolve the lot, select 'Passed', 'Rejected', or 'Expired'.");
           // browser.sleep(5000);
        });
        
        it('change status to Passed and resolve lot', function() {
            element(by.css('.lot-status')).element(by.cssContainingText('option', 'Passed')).click();
            element(by.css('.submit-button')).click();
            
            element(by.css('.resolve-another-box')).click();
            browser.sleep(5000);
        });
        
        
    });


});  
        


