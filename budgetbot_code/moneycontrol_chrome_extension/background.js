// Copyright (c) 2011 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

// Called when the user clicks on the browser action.
chrome.browserAction.onClicked.addListener(function(tab) {
  // No tabs or host permissions needed!
  console.log('Turning ' + tab.url + ' red!');
  chrome.tabs.executeScript({
    code: 'console.log(\'chus\');document.body.style.backgroundColor="red"'
  });
});



$(".btn_search").attr("onclick", "");
$(".btn_search").on("click", function(){
  // console.log("search click")
  text = $(".txtsrchbox").val()
  $.get("http://localhost:3000/master?question="+ text, function(data){
    window.mama = data
  })
})
