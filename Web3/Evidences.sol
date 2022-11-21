pragma solidity ^0.6.1;

contract Evidences{
	string case_id;
	string evd_no;
	string evd_img_ipfs_hash;
	string evd_text1;
	string evd_text2;
	string date;
	string time;
	constructor(string memory _case_id, string memory _evd_no, string memory _evd_img_ipfs_hash,
				string memory _evd_text1, string memory _evd_text2, string memory _date,
				string memory _time) public {
		case_id = _case_id;
		evd_no = _evd_no;
		evd_img_ipfs_hash = _evd_img_ipfs_hash;
		evd_text1 = _evd_text1;
		evd_text2 = _evd_text2;
		date = _date;
		time = _time;
	}
	function getEvdNo() public view returns(string memory){
		return evd_no;
	}
	function getEvdtext1() public view returns (string memory){
		return evd_text1;
	}
	function getEvdtext2() public view returns (string memory){
		return evd_text2;
	}
	function getCaseID() public view returns (string memory){
		return case_id;
	}
	function getEvidenceIpfs() public view returns (string memory){
		return evd_img_ipfs_hash;
	}
	function getDate() public view returns (string memory){
		return date;
	}
	function getTime() public view returns (string memory){
		return time;
	}
}