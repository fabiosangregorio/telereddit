asm telereddit_after_ma

import StandardLibrary
import CTLlibrary
import LTLlibrary

signature:
	// ### DOMAINS ###
	enum domain Status = {WAITING | DELETE_POST | EDIT_POST | MORE_POSTS | SEND_LINK | SEND_SUBREDDIT}
	enum domain ChooseStatus = {CHOOSE_DELETE_POST | CHOOSE_EDIT_POST | CHOOSE_MORE_POSTS | CHOOSE_SEND_LINK | CHOOSE_SEND_SUBREDDIT}
	enum domain ApiStatus = {OK | ERROR | API}
	enum domain PostId = {INVALID_POST | VALID_POST | NONE}
	domain Tries subsetof Integer
		
	// ### DYNAMIC FUNCTIONS ###
	dynamic controlled status: Status
	dynamic controlled apiStatus: ApiStatus
	dynamic controlled postId: PostId
	dynamic controlled tries: Tries

	dynamic monitored getPostId: PostId // if 0 then the api status will be ERROR
	dynamic monitored chooseStatus: ChooseStatus
	
	// ### STATIC FUNCTIONS ###
	derived triesLeft: Tries -> Tries

definitions:
	// ### DOMAIN DEFINITIONS ###
	domain Tries = {0..3}
	
	// ### FUNCTION DEFINITIONS ###
	// Return the number of attempts left before confirming API error
	function triesLeft($t in Tries) =
		3 - $t

	// ### RULE DEFINITIONS ###
	macro rule r_waiting = 
		if status = WAITING then
			par
				// Reset state
				if tries != 0 then
					tries := 0
				else
					skip
				endif
				postId := NONE
				if not(apiStatus = API) then
					apiStatus := API
				else
					skip
				endif
				
				switch(chooseStatus)
					case CHOOSE_DELETE_POST:
						status := DELETE_POST
					case CHOOSE_EDIT_POST:
						status := EDIT_POST
					case CHOOSE_MORE_POSTS:
						status := MORE_POSTS
					case CHOOSE_SEND_LINK:
						status := SEND_LINK
					case CHOOSE_SEND_SUBREDDIT:
						status := SEND_SUBREDDIT
				endswitch
			endpar
		else
			skip
		endif
		
	macro rule r_api =
		if apiStatus = API then
			seq
				postId := getPostId
				if postId = INVALID_POST and apiStatus = OK then
					apiStatus := ERROR
				else
					if apiStatus = ERROR then
						apiStatus := OK
					else
						skip
					endif
				endif
			endseq
		else
			skip
		endif
	
	macro rule r_sendPost =
		if status = SEND_LINK or status = SEND_SUBREDDIT then
			if not(apiStatus = API) then
				apiStatus := API
			else
				if not(status = SEND_SUBREDDIT) or apiStatus = OK then
					status := WAITING
				else
					skip
				endif
			endif
		else
			skip
		endif
		
	macro rule r_sendSubreddit =
		if status = SEND_SUBREDDIT then
			seq
				tries := tries + 1
				if triesLeft(tries) = 0 then
					status := WAITING
				else
					skip
				endif
			endseq
		else
			skip
		endif
			
	macro rule r_deletePost =
		if status = DELETE_POST then
			status := WAITING
		else
			skip
		endif
		
		
	macro rule r_editPost =
		if status = EDIT_POST then
			if not(apiStatus = API) then
				apiStatus := API
			else
				seq
					tries := tries + 1
					if triesLeft(tries) = 0 or apiStatus = OK then
						status := WAITING
					else
						skip
					endif
				endseq
			endif
		else
			skip
		endif

	// ### INVARIANTS ###
	// Never have OK API status and invalid post id
	invariant inv_api_invalid over apiStatus, postId, status: not(status = WAITING and apiStatus = OK and postId = INVALID_POST)
	// Never have ERROR API status and valid post id
	invariant inv_api_valid over apiStatus, postId, status: not(status = WAITING and apiStatus = ERROR and postId != INVALID_POST)
	
	CTLSPEC eg((status != WAITING and apiStatus = ERROR) implies ex(status = WAITING))
	LTLSPEC u(apiStatus = ERROR, postId != INVALID_POST)
	
	// ### MAIN RULE ###
	main rule r_Main =
		// Run actions
		par
			r_api[]
			r_waiting[]
			r_sendPost[]
			r_sendSubreddit[]
			r_deletePost[]
			r_editPost[]
		endpar
		
// ### INITIAL STATE ###
default init s0:
	function status = SEND_LINK
