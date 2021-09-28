import React from 'react'
import { axiosMultipartInstance } from '../../database/axios'
import loadgif from '../../assets/loading.gif'
import { Redirect } from 'react-router-dom'

class AccountDetail extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            username: props.match.params.username,
            first_name: '',
            last_name: '',
            email: '',
            profile_pic: null,
            about: '',

            is_admin: false,
            can_edit: false,
            wallets: [],

            loading: true,
            redirect: true,
        }
    }
    componentDidMount() {
        axiosMultipartInstance.get(`/accounts/${this.state.username}`)
            .then((response) => response.data)
            .then((data) => {
                this.setState({ ...data, loading: false })
            })
            .catch((errors) => {
                console.log(errors.data)
                this.setState({ redirect: true })
            })
    }

    render() {
        if (this.state.loading) {
            return <div className="flex-container align-center"><img src={loadgif}></img></div>
        }
        if (this.redirect) {
            return <Redirect to="/"></Redirect>
        }

        return (
            <div className="order-detail-section grid-container-outer" style={{ marginTop: "110px" }}>
                Hello, {this.state.username}
            </div>
        )
    }
}

export default AccountDetail;