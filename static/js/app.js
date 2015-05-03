var app = angular.module('MMQbeta', []);

app.run(function () {
});


app.config( function ($httpProvider) {
  delete $httpProvider.defaults.headers.common['X-Requested-With'];
});

app.filter("runningTotal", function () {
    return function(items, field, index) {
        var total = 0, i = 0;
        for (i = 0; i < index+1; i++) {
            total += items[i][field];
        }
        return total;
    };
});

app.filter("secondsToTime", function () {
    return function(seconds) {
        var div = Math.floor(seconds/60);
        var rem = seconds % 60;
        if(rem < 10) {
            rem = "0" + rem;
        }
        return div + ":" +rem;
    };
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
    playerHeight: '280',
    playerWidth: '100%',
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
    service.launchPlayer(upcoming[0].code, upcoming[0].title);
    service.archiveVideo(upcoming[0].r_id);
    $rootScope.loading -= 1;
    service.poll();
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
        service.launchPlayer(upcoming[0].code, upcoming[0].title);
        service.archiveVideo(upcoming[0].r_id);
    }
    $rootScope.$apply();
  }

  this.startPlaylistPoll =  function () {
      service.playlistPoll();
      $timeout(service.startPlaylistPoll, 10000);
  };

  this.playlistPoll = function () {
      var d = $http.get("/" + service.channel + '/playlist');
        // Call the async method and then do stuff with what is returned inside our own then function
        d.then(function(d) {
            playlist.length = 0;
            playlist.push.apply(playlist, d.data.playlistVideos);
            upcoming.length = 0;
            upcoming.push.apply(upcoming, d.data.upcoming);
            youtube.videoTitle = d.data.current_title;
            $rootScope.header = d.data.current_title;
        });
  };

  this.startPoll =  function () {
      service.poll();
      $timeout(service.startPoll, 5000);
  };

  this.poll =  function () {
        var d = $http.get("/" + service.channel + '/results');
        // Call the async method and then do stuff with what is returned inside our own then function
        d.then(function(d) {
            upcoming.length = 0;
            upcoming.push.apply(upcoming, d.data.videos);
        });
  };

  this.pushState = function () {
      $log.info('Youtube API status is changed');
  };

  this.map = function(lambda, values) {
         switch (values.length) {
            case 0: return values;
            case 1: return [lambda(values.shift())];
            default: return [lambda(values.shift())].concat(this.map(lambda, values));
         }
  };

  this.listResults = function(data) {
       rewrite = function(entry) {return {
            'id': entry.id.videoId,
            'title': entry.snippet.title,
            'thumbnail': entry.snippet.thumbnails.default.url
       }};
      results.length = 0;
      results.push.apply(results, this.map(rewrite, data.items));
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
        showinfo: 1
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
    $log.log(id,title);
    youtube.player.loadVideoById(id);
    youtube.videoId = id;
    youtube.videoTitle = title;
    return youtube;
  };

  this.queueVideo = function (id, title, r_id) {
    upcoming.push({
      id: id,
      title: title,
      r_id: r_id
    });
    return upcoming;
  };

  this.archiveVideo = function (id) {
      $http.post('/' + service.channel + '/finish', {"id": id}).
        success(function (results) {
        }).
        error(function (error) {
            $log.log(error);
        });
  };

  this.deleteVideo = function (list, id) {
    for (var i = list.length - 1; i >= 0; i--) {
      if (list[i].code === id) {
        list.splice(i, 1);
        break;
      }
    }
  };

  this.getResults = function () {
      return results;
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

app.controller('IndexController', function ($scope, $http, $log,$timeout, $rootScope, VideosService) {
    init();

   function init() {
      $scope.playlist = VideosService.getPlaylist();
      $scope.upcoming = VideosService.getUpcoming();
      $scope.results = VideosService.getResults();
      $scope.youtube = VideosService.getYoutube();
      $scope.playing = false;
      $rootScope.loading = 0;
    };

    $scope.search = function () {
      $http.get('https://www.googleapis.com/youtube/v3/search', {
        params: {
          key: 'AIzaSyBI27WBKxhL4TUZ1XAiPK5Z9CPBRfx7iKA',
          type: 'video',
          maxResults: '8',
          part: 'id,snippet',
          fields: 'items/id,items/snippet/title,items/snippet/description,items/snippet/thumbnails/default,items/snippet/channelTitle',
          q: this.query
        }
      })
      .success( function (data) {
        VideosService.listResults(data);
        $log.info(data);
      })
      .error( function () {
        $log.info('Search error');
      });
    }


    $scope.init = function() {
       VideosService.channel = $scope.channel;
       VideosService.startPlaylistPoll();
    };

    $scope.changeState = function () {
        VideosService.changeState();
    }

    $scope.launch = function (code, title, r_id) {
        if($scope.playing == true) {
            VideosService.launchPlayer(code, title);
            VideosService.archiveVideo(r_id);
            VideosService.poll();
            $log.info('Launched id:' + code + ' and title:' + title);
        } else {
            $log.log("nop kan niet");
        }
    };

    $scope.queue = function (id) {
      $http.post('/' + $scope.channel + '/add_existing', {"id": id}).
        success(function(results) {
            VideosService.poll();
        }).
        error(function(error) {
          $log.log(error);
        });
    }
    $scope.remove = function(r_id) {
        $http.post('/'+$scope.channel + '/remove' ,{"id": r_id}).
            success(function(results) {
                VideosService.poll();
            }).
            error(function(error) {
              $log.log(error);
            });
    };

    $scope.add = function (id) {
      $http.post('/' + $scope.channel + '/add', {"id": id}).
        success(function(results) {
            $scope.query = "";
            $scope.results.length = 0;
            VideosService.poll();
        }).
        error(function(error) {
          $log.log(error);
        });
    };

    $scope.startBroadcast = function() {
        if($scope.playing == false) {
            VideosService.startPoll();
            $rootScope.loading += 1;
            var tag = document.createElement('script');
            tag.src = "http://www.youtube.com/iframe_api";
            var firstScriptTag = document.getElementsByTagName('script')[0];
            firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
            $scope.playing = true;
        }
    }

});