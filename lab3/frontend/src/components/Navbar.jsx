import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import React from 'react';
import { axiosInstance } from '../database/axios'
import { Link } from 'react-router-dom'


class Navbar extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            currentUser: null,
            authToken: null,
        }
        this.timerID = null
    }
    componentDidMount() {
        this.timerID = setInterval(() => {
            const newToken = window.localStorage.getItem("access_token")
            if (newToken === this.state.authToken) {
                return;
            }

            axiosInstance.get("profile/")
                .then((response) => response.data)
                .then((data) => {
                    this.setState({
                        currentUser: { ...data },
                        authToken: newToken,
                    })
                })
                .catch((errors) => {
                    console.log(errors.response.data)
                    this.setState({
                        currentUser: null,
                        authToken: null,
                    })
                })
        }, 500)
    }
    componentWillUnmount() {
        clearInterval(this.timerID)
        this.timerID = null
    }

    isLoggedIn = () => {
        return this.state.currentUser !== null
    }


    render() {
        return (
            <nav className="navbar">
                {
                    this.isLoggedIn()
                        ?
                        <ul className="flex-container align-right inverse-center">
                            <li key="hello" style={{ fontSize: "2rem", fontStyle: "italic" }} className="greeting">
                                Добро пожаловать, {this.state.currentUser.username}
                            </li>
                            <li key="home" className="nav-item">
                                <Link to="/">
                                    <FontAwesomeIcon icon={['fas', 'igloo']} style={{ fontSize: "4rem" }}></FontAwesomeIcon>
                                </Link>
                            </li>
                            <li key="profile" className="nav-item">
                                <Link to={`/accounts/${this.state.currentUser.username}`}>
                                    <img src={this.state.currentUser.profile_pic} className="round-thumbnail-75"></img>
                                </Link>
                            </li>
                            <li key="logout" className="nav-item">
                                <Link to="/accounts/logout">
                                    <FontAwesomeIcon icon={['fas', 'sign-out-alt']} rotation={180} style={{ fontSize: "4rem" }}></FontAwesomeIcon>
                                </Link>
                            </li>
                        </ul>
                        :
                        <ul className="nav-item-container flex-container align-right inverse-center">
                            <li key="home" className="nav-item">
                                <Link to="/">
                                    <FontAwesomeIcon icon={['fas', 'igloo']} style={{ fontSize: "4rem" }}></FontAwesomeIcon>
                                </Link>
                            </li>
                            <li key="login" className="nav-item">
                                <Link to="/accounts/login">
                                    <FontAwesomeIcon icon={['fas', 'sign-in-alt']} style={{ fontSize: "4rem" }}></FontAwesomeIcon>
                                </Link>
                            </li>
                            <li key="register" className="nav-item">
                                <Link to="/accounts/register">
                                    <FontAwesomeIcon icon={['fas', 'user-plus']} style={{ fontSize: "4rem" }}></FontAwesomeIcon>
                                </Link>
                            </li>
                        </ul>
                }
            </nav>
        )
    }
}

export default Navbar;