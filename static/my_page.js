
document.addEventListener("DOMContentLoaded", function() {

    var btnPwChangeHTML = document.getElementById("pwHtmlChange");
    var btnMemOutHTML = document.getElementById("memOutHTMLChange")

    // Change HTMTL for changing pw.
    btnPwChangeHTML.addEventListener("click", function(event) {

        pwChangeForm();
        var btnChangePw = document.getElementById("formPw")
        btnChangePw.addEventListener("submit", function(event) { validateInputAndSend(); });

    });




    // change HTML for Member Out
    btnMemOutHTML.addEventListener("click", function(event) {

        memOutChangeForm();
        var btnMemOut = document.getElementById("formMemout")
        btnMemOut.addEventListener("submit", function(event) { memOut(); });

    });




});


 function memOut() {

    var pw = document.getElementById("memOutPw").value;

    if (pw.length == 0){
        alert("입력되지 않은 정보가 있습니다.")
        flag = false;
        event.preventDefault();
    }else
    {
        pwSha = SHA256(pw);
        document.getElementById("memOutPw").value = pwSha;
    }
 }

 function memOutChangeForm() {
    var memOutTd = document.getElementById('memOut');

    memOutTd.innerHTML = `
    <form action="/my_page" method="POST" id="formMemout">
        <table>
            <tr>
                <td class="pwKey"><span class="smlTxt"><span class="red">*</span> 계정 비밀번호</span></td>
                <td class="pwVal"><input class="pw" type="password" name="memOutPw", id="memOutPw"></td>
            </tr>
        </table>
        <div class="inputPw"><button type="submit", id="pwChange" class="btnInner"><span class="red">회원 탈퇴</span></button></div>
    </form>`;
 }







 // Function to validate user input for changing password and send input to server
 function validateInputAndSend() {
    var prePw = document.getElementById("prePw").value;
    var newPw = document.getElementById("newPw").value;
    var newPw2 = document.getElementById("newPw2").value;
    var regex = /^[0-9a-zA-Z!@#$%^&]+$/;
    var flag = true;

    function check_Qualification(value, min, max, regex) {
      return value.length >= min && value.length <= max && regex.test(value);
    }

    if ( prePw.length == 0 | newPw.length == 0 | newPw2.length == 0 ){
        alert("입력되지 않은 정보가 있습니다.")
        flag = false;
        event.preventDefault();
    }

    else if ( newPw != newPw2 ) {
        alert("변경할 비밀번호가 일치하지 않습니다.");
        flag = false;
        event.preventDefault();
    }

    else if ( prePw == newPw | prePw == newPw2 )
    {
        alert("변경할 비밀번호가 이전의 비밀번호와 동일합니다.");
        flag = false;
        event.preventDefault();
    }

    else if ( !check_Qualification(newPw, 5, 15, regex) | !check_Qualification(newPw2, 5, 15, regex)){
        alert("입력하신 password가 유효하지 않습니다.\n5~15 길이의 영문, 숫자, 특수문자(!@#$%^&)의 조합으로 작성해주세요");
        flag = false;
        event.preventDefault();
    }

    if ( flag ) {
        prePwSha = SHA256(prePw);
        newPwSha = SHA256(newPw);
        newPw2Sha = SHA256(newPw2);

        document.getElementById("prePw").value = prePwSha;
        document.getElementById("newPw").value = newPwSha;
        document.getElementById("newPw2").value = newPw2Sha;
    }
    else
    {
        document.getElementById("newPw").value = '';
        document.getElementById("newPw2").value = '';
    }
 }

 // Function to change HTML in div#changePwTd
 function pwChangeForm() {
    var changePwTd = document.getElementById('changePW');

    changePwTd.innerHTML = `
        <form action="/my_page" method="POST", id="formPw">
            <table>
                <tr>
                    <td class="pwKey"><span class="smlTxt"><span class="red">*</span> 기존 비밀번호</span></td>
                    <td class="pwVal"><input class="pw" type="password" name="prePw", id="prePw"></td>
                </tr>
                <tr>
                    <td class="pwKey"><span class="smlTxt"><span class="red">*</span> 변경할 비밀번호</span></td>
                    <td class="pwVal"><input class="pw" type="password" name="newPw", id="newPw"></td>
                </tr>
                <tr>
                    <td class="pwKey"><span class="smlTxt"><span class="red">*</span> 변경 비밀번호 재입력</span></td>
                    <td class="pwVal"><input class="pw" type="password" name="newPw2", id="newPw2"></td>
                </tr>
            </table>
            <hr>
            <div class="inputPw"><button type="submit", id="pwChange" class="btnInner"> 비밀번호 변경 </button></div>
        </form>
    `;
  }

 function check_Qualification(value, min, max, regex) {
   return value.length >= min && value.length <= max && regex.test(value);
 }

  // Functions relate with Javascript SHA256 Encryption
  // DO NOT ERASE
  function SHA256(s){
   var chrsz = 8;
   var hexcase = 0;

   function safe_add (x, y) {
   var lsw = (x & 0xFFFF) + (y & 0xFFFF);
   var msw = (x >> 16) + (y >> 16) + (lsw >> 16);
   return (msw << 16) | (lsw & 0xFFFF);
   }

  function S (X, n) { return ( X >>> n ) | (X << (32 - n)); }
  function R (X, n) { return ( X >>> n ); }
  function Ch(x, y, z) { return ((x & y) ^ ((~x) & z)); }
  function Maj(x, y, z) { return ((x & y) ^ (x & z) ^ (y & z)); }
  function Sigma0256(x) { return (S(x, 2) ^ S(x, 13) ^ S(x, 22)); }
  function Sigma1256(x) { return (S(x, 6) ^ S(x, 11) ^ S(x, 25)); }
  function Gamma0256(x) { return (S(x, 7) ^ S(x, 18) ^ R(x, 3)); }
  function Gamma1256(x) { return (S(x, 17) ^ S(x, 19) ^ R(x, 10)); }

  function core_sha256 (m, l) {
   var K = new Array(0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5, 0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174, 0xE49B69C1, 0xEFBE4786, 0xFC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA, 0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x6CA6351, 0x14292967, 0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85, 0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070, 0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3, 0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2);
   var HASH = new Array(0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19);
   var W = new Array(64);
   var a, b, c, d, e, f, g, h, i, j;
   var T1, T2;

   m[l >> 5] |= 0x80 << (24 - l % 32);
   m[((l + 64 >> 9) << 4) + 15] = l;

   for ( var i = 0; i<m.length; i+=16 ) {
   a = HASH[0];
   b = HASH[1];
   c = HASH[2];
   d = HASH[3];
   e = HASH[4];
   f = HASH[5];
   g = HASH[6];
   h = HASH[7];

   for ( var j = 0; j<64; j++) {
   if (j < 16) W[j] = m[j + i];
   else W[j] = safe_add(safe_add(safe_add(Gamma1256(W[j - 2]), W[j - 7]), Gamma0256(W[j - 15])), W[j - 16]);

   T1 = safe_add(safe_add(safe_add(safe_add(h, Sigma1256(e)), Ch(e, f, g)), K[j]), W[j]);
   T2 = safe_add(Sigma0256(a), Maj(a, b, c));

   h = g;
   g = f;
   f = e;
   e = safe_add(d, T1);
   d = c;
   c = b;
   b = a;
   a = safe_add(T1, T2);
   }

   HASH[0] = safe_add(a, HASH[0]);
   HASH[1] = safe_add(b, HASH[1]);
   HASH[2] = safe_add(c, HASH[2]);
   HASH[3] = safe_add(d, HASH[3]);
   HASH[4] = safe_add(e, HASH[4]);
   HASH[5] = safe_add(f, HASH[5]);
   HASH[6] = safe_add(g, HASH[6]);
   HASH[7] = safe_add(h, HASH[7]);
   }
   return HASH;
 }

 function str2binb (str) {
   var bin = Array();
   var mask = (1 << chrsz) - 1;
   for(var i = 0; i < str.length * chrsz; i += chrsz) {
   bin[i>>5] |= (str.charCodeAt(i / chrsz) & mask) << (24 - i % 32);
   }
   return bin;
  }

 function Utf8Encode(string) {
   string = string.replace(/\r\n/g,'\n');
   var utftext = '';

   for (var n = 0; n < string.length; n++) {

   var c = string.charCodeAt(n);

   if (c < 128) {
     utftext += String.fromCharCode(c);
     }
     else if((c > 127) && (c < 2048)) {
     utftext += String.fromCharCode((c >> 6) | 192);
     utftext += String.fromCharCode((c & 63) | 128);
     }
     else {
     utftext += String.fromCharCode((c >> 12) | 224);
     utftext += String.fromCharCode(((c >> 6) & 63) | 128);
     utftext += String.fromCharCode((c & 63) | 128);
     }
   }

   return utftext;
 }

 function binb2hex (binarray) {
   var hex_tab = hexcase ? '0123456789ABCDEF' : '0123456789abcdef';
   var str = '';
   for(var i = 0; i < binarray.length * 4; i++) {
   str += hex_tab.charAt((binarray[i>>2] >> ((3 - i % 4)*8+4)) & 0xF) +
   hex_tab.charAt((binarray[i>>2] >> ((3 - i % 4)*8 )) & 0xF);
   }
   return str;
   }

   s = Utf8Encode(s);
   return binb2hex(core_sha256(str2binb(s), s.length * chrsz));
}