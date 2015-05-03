var app = angular.module('MMQbeta', []);

app.run(function () {
  var tag = document.createElement('script');
  tag.src = "http://www.youtube.com/iframe_api";
  var firstScriptTag = document.getElementsByTagName('script')[0];
  firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
});

app.config( function ($httpProvider) {
  delete $httpProvider.defaults.headers.common['X-Requested-With'];
});

app.controller('IndexController', function ($scope, $http, $log) {
    init();

    function init() {
        var channels =[];
        $scope.channels = channels;
        $log.log($scope.channels);
    }
    $scope.poll = function() {
      var d = $http.get("/channels");
        // Call the async method and then do stuff with what is returned inside our own then function
        d.then(function(d) {
            $log.log(d);
            $scope.channels.length = 0;
            $scope.channels.push.apply($scope.channels, d.data.channels);
            $log.log($scope.channels);
        });

    }
    $scope.add = function () {
      $http.post('/add', {"title": $scope.channel}).
        success(function(results) {
            $scope.channel = "";
            $scope.poll();
        }).
        error(function(error) {
          $log.log(error);
        });
    };

});