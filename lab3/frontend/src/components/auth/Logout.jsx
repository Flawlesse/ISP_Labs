import { Redirect } from "react-router-dom";


const Logout = (props) => {
    const logout = props.appLogout
    logout()
    return <Redirect to="/"></Redirect>
}



export default Logout;