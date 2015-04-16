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

app.service('VideosService', ['$window', '$rootScope', '$log', '$http', '$timeout', function ($window, $rootScope, $log, $http, $timeout) {
  var service = this;
  var channel;
  var youtube = {
    ready: false,
    player: null,
    playerId: null,
    videoId: null,
    videoTitle: null,
    playerHeight: '480',
    playerWidth: '640',
    state: 'stopped'
  };
  var results = [];
  var upcoming = [];
  var playlist = [];
  $window.onYouTubeIframeAPIReady = function () {
    $log.info('Youtube API is ready');
    youtube.ready = true;
    service.bindPlayer('placeholder');
    service.loadPlayer();
    $rootScope.$apply();
  };

  function onYoutubeReady (event) {
    $log.info('YouTube Player is ready');
  }

  function onYoutubeStateChange (event) {
    if (event.data == YT.PlayerState.PLAYING) {
      youtube.state = 'playing';
      service.pushState();
    } else if (event.data == YT.PlayerState.PAUSED) {
      youtube.state = 'paused';
      service.pushState();
    } else if (event.data == YT.PlayerState.ENDED) {
        youtube.state = 'ended';
        service.launchPlayer(upcoming[0].id, upcoming[0].title);
        service.archiveVideo(upcoming[0].r_id);
        service.deleteVideo(upcoming, upcoming[0].id);
    }
    $rootScope.$apply();
  }

  this.startPoll =  function () {
        var d = $http.get("/" + service.channel + '/results');
        // Call the async method and then do stuff with what is returned inside our own then function
        d.then(function(d) {
            playlist.length = 0
            playlist.push.apply(playlist, d.data.videos);
        });
        $log.log(playlist);
        $timeout(service.startPoll, 5000)
  };
  this.pushState = function () {
      $log.info('Youtube API status is changed');
  };
  this.activate = function () {

  };
  this.bindPlayer = function (elementId) {
    $log.info('Binding to ' + elementId);
    youtube.playerId = elementId;
  };

  this.createPlayer = function () {
    $log.info('Creating a new Youtube player for DOM id ' + youtube.playerId + ' and video ' + youtube.videoId);
    return new YT.Player(youtube.playerId, {
      height: youtube.playerHeight,
      width: youtube.playerWidth,
      playerVars: {
        rel: 0,
        showinfo: 0
      },
      events: {
        'onReady': onYoutubeReady,
        'onStateChange': onYoutubeStateChange
      }
    });
  };

  this.loadPlayer = function () {
    if (youtube.ready && youtube.playerId) {
      if (youtube.player) {
        youtube.player.destroy();
      }
      youtube.player = service.createPlayer();
    }
  };

  this.launchPlayer = function (id, title) {
    youtube.player.loadVideoById(id);
    youtube.videoId = id;
    youtube.videoTitle = title;
    return youtube;
  }

  this.queueVideo = function (id, title, r_id) {
    upcoming.push({
      id: id,
      title: title,
      r_id: r_id
    });
    return upcoming;
  };

  this.archiveVideo = function (id) {
      $log.log(id);
    $http.post('/' + service.channel + '/finish', {"id": id}).
        success(function (results) {
            $log.log(results);
        }).
        error(function (error) {
            $log.log(error);
        });
  };

  this.deleteVideo = function (list, id) {
    for (var i = list.length - 1; i >= 0; i--) {
      if (list[i].id === id) {
        list.splice(i, 1);
        break;
      }
    }
  };
  this.getTitle = function(id) {
      var d = $http.jsonp('http://gdata.youtube.com/feeds/api/videos/'+ id + '?alt=json-in-script&callback=JSON_CALLBACK&prettyprint=true&fields=title');
      return d;
  };

  this.getYoutube = function () {
    return youtube;
  };
  this.getPlaylist = function () {
    return playlist;
  };
  this.getUpcoming = function () {
    return upcoming;
  };
}]);

// Controller
app.controller('VideosController', function ($scope, $http, $log,$timeout, VideosService) {
    init();

   function init() {
      $scope.youtube = VideosService.getYoutube();
      $scope.upcoming = VideosService.getUpcoming();
      $scope.playlist = true;
      $scope.maxId = 0;
    }

    $scope.changeState = function () {
        VideosService.changeState();
    }

    $scope.init = function() {
       VideosService.channel = $scope.channel;
       $log.log(VideosService.channel);
       this.getData();
    }

    $scope.getData = function() {
        var d = $http.get("/" + $scope.channel + '/results');
        // Call the async method and then do stuff with what is returned inside our own then function
        d.then(function(d) {
            d.data.videos.forEach(function (vid) {
                if (vid['r_id'] > $scope.maxId) {
                    $scope.queue(vid['code'], vid['title'], vid['r_id']);
                    $scope.maxId = vid['r_id'];
                };
            });
        });
        $timeout(function() {$scope.getData()}, 5000)
    };


    $scope.launch = function (id, title, r_id) {
      VideosService.launchPlayer(id, title);
      VideosService.archiveVideo(r_id);
      VideosService.deleteVideo($scope.upcoming, id);
      $log.info('Launched id:' + id + ' and title:' + title);
    };

    $scope.queue = function (id, title, r_id) {
      VideosService.queueVideo(id, title, r_id);
      $log.info('Queued id:' + r_id + ' and title:' + title);
    };

    $scope.add = function () {
      $http.post('/' + $scope.channel + '/add', {"id": this.query}).
        success(function(results) {
         $scope.query = "";
        }).
        error(function(error) {
          $log.log(error);
        });
    };

    $scope.tabulate = function (state) {
      $scope.playlist = state;
    }
});
app.controller('IndexController', function ($scope, $http, $log,$timeout, VideosService) {
    init();

   function init() {
      $scope.playlist = VideosService.getPlaylist();
    }

    $scope.init = function() {
       VideosService.channel = $scope.channel;
       VideosService.startPoll();
    };

    $scope.add = function () {
      $http.post('/' + $scope.channel + '/add', {"id": this.query}).
        success(function(results) {
            $scope.query = "";
        }).
        error(function(error) {
          $log.log(error);
        });
    }

});