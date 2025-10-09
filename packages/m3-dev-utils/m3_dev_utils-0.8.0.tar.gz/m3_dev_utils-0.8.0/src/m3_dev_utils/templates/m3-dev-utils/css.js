// Добавление CSS-классов для окон приложения.

(function() {
    var cssStyleSheet = document.styleSheets[0];
    var cssRules = cssStyleSheet.cssRules;

    function insertRule(selector, rule) {
        for (var i = 0; i < cssRules.length; i++) {
            if (cssRules[i].selectorText == selector) {
                return;
            }
        }

        cssStyleSheet.insertRule(selector + ' ' + rule, cssRules.length);
    }

    insertRule('.m3-dev-utils-red *',  '{color: red !important}');
    insertRule('.m3-dev-utils-monospace', '{font-family: monospace}');
})();
