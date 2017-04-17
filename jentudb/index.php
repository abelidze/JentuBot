<?php
	function adminer_object() {
		class AdminerSoftware extends Adminer {
			
			function name() {
				return 'JentuDB';
			}
			
			function login($login, $password) {
				return ($login == 'arios' && $password == 'jentu');
			}
			
			function loginForm() {
				echo '<table cellspacing="0">
				<tr><th>' . lang("Username") . '</th> <td><input name="auth[username]" id="username" autocapitalize="off"/></td> </tr>
				<tr><th>' . lang('Password') . '</th> <td><input name="auth[password]" type="password" /></td> </tr>
				</table>
				<script type="text/javascript">
					focus(document.getElementById("username"));
				</script>
				';
				echo '<p><input type="submit" value="' . lang('Login') . '" /></p>';
				echo '<input name="auth[driver]" type="hidden" value="sqlite" />';
				echo '<input name="auth[db]" type="hidden" value="jentu.db" />';
			}
		}
		return new AdminerSoftware;
	}
	include "./adminer/include.php";
?>