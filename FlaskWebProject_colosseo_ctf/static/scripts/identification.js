function r() {
            var username = document.getElementById("username");
            var password = document.getElementById("password");
            if (username.value == "") {
                alert("请输入用户名");
                username.focus();
                return;
            }
            if (password.value == "") {
                alert("请输入密码");
                return;
            }
			/*
			这里用来实名认证
			for search local database;
			information insert from pre;
			*/
		    var res = verifyCode.validate(document.getElementById("code_input").value);
		    if(res){
		        
		    }else{
                alert("验证码错误");
                return;
		    }
            return true;
        }