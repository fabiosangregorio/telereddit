asm telereddit

import StandardLibrary
import CTLlibrary
import LTLlibrary

signature:
	// ### DOMAINS ###
	enum domain Status = {WAITING | DELETE_POST | EDIT_POST | MORE_POSTS | SEND_LINK | SEND_SUBREDDIT}
	enum domain ApiStatus = {OK | ERROR}
	domain Tries subsetof Integer
	domain PostId subsetof Integer
		
	// ### DYNAMIC FUNCTIONS ###
	dynamic controlled status: Status
	dynamic controlled apiStatus: ApiStatus
	dynamic controlled postId: PostId
	dynamic controlled tries: Tries
	
	dynamic monitored getPostId: PostId // if 0 then the api status will be ERROR
	dynamic monitored chooseStatus: Status
	
	// ### STATIC FUNCTIONS ###
	derived triesLeft: Tries -> Tries

definitions:
	// ### DOMAIN DEFINITIONS ###
	domain Tries = {0..3}
	domain PostId = {0..10} // 0 is reserved for API error, 10 is reserved for API waiting
	
	// ### FUNCTION DEFINITIONS ###
	// Return the number of attempts left before confirming API error
	function triesLeft($t in Tries) =
		3 - $t

	// ### RULE DEFINITIONS ###
	rule r_sendPost =
		// Simulate API error with postId = 0
		seq
			postId := getPostId
			if postId = 0 then
				apiStatus := ERROR
			else
				apiStatus := OK
			endif
			if not(status = SEND_SUBREDDIT) or apiStatus = OK then
				status := WAITING
			endif
		endseq
		
	rule r_sendSubreddit =
		seq
			tries := tries + 1
			if triesLeft(tries) = 0 then
				status := WAITING
			endif
		endseq
			
	rule r_deletePost =
		seq
			postId := 10
			status := WAITING
		endseq
		
	rule r_editPost =
		seq
			postId := getPostId
			if postId = 0 then
				apiStatus := ERROR
			else
				apiStatus := OK
			endif
			tries := tries + 1
			if triesLeft(tries) = 0 or apiStatus = OK then
				status := WAITING
			endif
		endseq

	// ### INVARIANTS ###
	// Never have OK API status and invalid post id
	invariant inv_api_invalid over apiStatus, postId, status: not(status = WAITING and apiStatus = OK and postId = 0)
	// Never have ERROR API status and valid post id
	invariant inv_api_valid over apiStatus, postId, status: not(status = WAITING and apiStatus = ERROR and postId != 0)
	
	CTLSPEC eg((status != WAITING and apiStatus = ERROR) implies ex(status = WAITING))
	LTLSPEC u(apiStatus = ERROR, postId != 0)
	
	// ### MAIN RULE ###
	main rule r_Main =
		// Run actions
		switch(status)
			case WAITING:
				par
					// Reset state
					tries := 0
					postId := 10
					apiStatus := OK
					status := chooseStatus
				endpar
			case MORE_POSTS:
				status := SEND_SUBREDDIT
			case SEND_LINK: r_sendPost[]
			case SEND_SUBREDDIT: 
				par
					r_sendPost[]
					r_sendSubreddit[]
				endpar
			case DELETE_POST: r_deletePost[]
			case EDIT_POST: r_editPost[]
		endswitch
	
// ### INITIAL STATE ###
default init s0:
	function status = WAITING
