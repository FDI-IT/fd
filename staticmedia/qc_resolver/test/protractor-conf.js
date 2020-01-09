// exports.config = {
  // allScriptsTimeout: 11000,
// 
  // specs: [
    // 'e2e/*.js'
  // ],
// 
  // capabilities: {
    // 'browserName': 'firefox'
  // },
// 
  // firefoxOnly: true,
// 
  // baseUrl: 'http://localhost:8000/',
// 
  // framework: 'jasmine',
// 
  // jasmineNodeOpts: {
    // defaultTimeoutInterval: 30000
  // }
// };


exports.config = {
  allScriptsTimeout: 11000,

  specs: [
    'e2e/*.js'
  ],

  capabilities: {
    'browserName': 'chrome',
    'binary': '/usr/bin/chromium-browser'
  },

  chromeOnly: true,

  baseUrl: 'http://localhost/',

  framework: 'jasmine',

  jasmineNodeOpts: {
    defaultTimeoutInterval: 30000
  }
};
