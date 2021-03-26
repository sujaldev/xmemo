ham = document.getElementsByClassName('ham-menu')[0]
open_btn = document.getElementsByClassName('logo')[0]
close_btn = document.getElementsByClassName('sub close-ham')[0]
title_btn = document.getElementsByClassName('title')[0]
mode = document.getElementsByClassName('mode')[0]


title_btn.onclick = function(){
	if (mode.getAttribute('href') == "/static/css/light-theme.css"){
		mode.setAttribute('href', "/static/css/dark-theme.css")
	} else {
		mode.setAttribute('href', "/static/css/light-theme.css")
	}
}

open_btn.onclick = function(){
	ham.setAttribute('class', 'ham-menu ham-active')
}

close_btn.onclick = function(){
	ham.setAttribute('class', 'ham-menu')
}

