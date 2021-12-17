export const utilsMixin = {

  methods: {
    listLength(list) {
      if (!list) {
        return 0;
      }
      if (typeof(list) === "string") {
        return this.cleanSplit(list).length;
      }
      return list.length;
    },
    makeCopy(obj) {
      return JSON.parse(JSON.stringify(obj));
    },
    makeDASLink(dataset) {
      return 'https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D' + dataset;
    },
    cleanSplit(str) {
      if (!str || !str.length) {
        return [];
      }
      return str.replace(/,/g, '\n').split('\n').map(function(s) { return s.trim() }).filter(Boolean);
    },
    getError(response) {
      if (response.response && response.response.data.message) {
        return response.response.data.message;
      }
      return ('Error message could not be found in response, most likely SSO cookie has expired. ' +
              'Try clicking <a href="/rereco" target="blank">here</a>. ' +
              'This will open ReReco homepage in a new tab and hopefully refresh your SSO cookie. ' +
              'You can then close the newly opened tab, dismiss this alert and try performing same action again.');
    },
    stringifyLumis: function(lumis) {
      if (!lumis) {
        return '';
      }

      let outputLines = '';
      for (let run in lumis) {
        let ranges = lumis[run].map(JSON.stringify);
        let longestString = Math.max(...ranges.map(x => x.length));
        let line = '  "' + run + '": [';
        let indentation = ' '.repeat(line.length);
        let i = 0;
        for (let range of ranges) {
          line += range + ',' + ' '.repeat(longestString - range.length);
          i++;
          if (i % 5 == 0) {
            line += '\n' + indentation;
          }
        }
        line = line.trimRight().slice(0, -1) + '],\n'
        outputLines += line;
      }
      if (Object.keys(lumis).length != 0) {
        outputLines = '\n' + outputLines.trimRight().slice(0, -1) + '\n';
      }
      return '{' + outputLines + '}';
    },
    hasStep: function(obj, step) {
      for (let seq of obj.sequences) {
        let steps = seq.step;
        if (steps instanceof String) {
          steps = steps.split(',').map(x => x.split(':')[0]);
        }
        if (steps.includes(step)) {
          return true;
        }
      }
      return false;
    }
  }
}
