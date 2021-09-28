import { Redirect } from "react-router-dom"
import { axiosInstance } from "../../database/axios"
import React from 'react'
import loadgif from '../../assets/loading.gif'


class Profile extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            username: '',
        }
    }
    componentDidMount() {
        this.getProfileUsername()
            .then((username) => {
                this.setState({ loading: false, username })
            })
            .catch((errors) => {
                this.setState({ loading: false })
            })
    }

    getProfileUsername = async () => {
        const result = await axiosInstance.get("profile/")
        return await result.data.username
    }

    render() {
        if (this.state.loading) {
            return <div className="flex-container align-center"><img src={loadgif}></img></div>
        }
        if (this.state.username) {
            return <Redirect to={`/accounts/${this.state.username}`}></Redirect>
        }
        else {
            return <Redirect to="/"></Redirect>
        }
    }
}

export default Profile;