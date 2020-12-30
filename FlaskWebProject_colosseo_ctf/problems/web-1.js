function validate_required(field,alerttxt)
		{
		with (field)
		{
		  if (value==null||value=="")
			{alert(alerttxt);return false}

		  if(value=="We1c0m3t0Col0sseoCTFi3Ld")
			{alert("flag{We1c0m3t0Col0sseoCTFi3Ld}");return true}
		}
		}
		
		function validate_form(thisform)
		{
			with (thisform)
			{
			  if (validate_required(flag,"flag must be filled out!")==false)
				{flag.focus();return false}
			  if (validate_required(flag,"flag must be filled out!")==true)
				{return true}
			} 
		}