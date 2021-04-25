import React from 'react';
import thumbsup from './images/thumbsup.png';
import star from './images/star.png';
import './Poster.css';

const hostAddress = '192.168.0.188'
const serverPort = 8080

class Poster extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      index: null,
      titlePath: null,
      posterPath: null,
      title: null,
      ratingCount: null,
      ratingValue: null,
    }
  }

  getTitleData() {
    this.setState({
      index: parseInt(this.props.dataFromParent) + 1
    })

    fetch(`http://${hostAddress}:${serverPort}`)
      .then(response => {
        return response.text();
      })
      .then(data => {
        this.setTitle(JSON.parse(data)[this.props.dataFromParent]["name"]);
        this.setTitlePath(JSON.parse(data)[this.props.dataFromParent]["url"]);
        this.setPosterPath(JSON.parse(data)[this.props.dataFromParent]["poster_url"]);
        this.setRatingCount(JSON.parse(data)[this.props.dataFromParent]["rating_count"]);
        this.setRatingValue(JSON.parse(data)[this.props.dataFromParent]["rating_value"]);
      });
  }

  setTitle(title) {
    this.setState({
      title: title
    })
  }

  setTitlePath(titleUrl) {
    this.setState({
      titlePath: titleUrl
    })
  }

  setPosterPath(posterUrl) {
    this.setState({
      posterPath: posterUrl
    })
  }

  setRatingCount(ratingCount) {
    this.setState({
      ratingCount: ratingCount
    })
  }

  setRatingValue(ratingValue) {
    this.setState({
      ratingValue: ratingValue
    })
  }  

  componentDidMount() {
    this.getTitleData();
    this.setTitle();
    this.setPosterPath();
    this.setRatingCount();
    this.setRatingValue();
  }

  render() {
    return (
      <div className='title-body'>
        <div className='title-poster'>
          <img src={this.state.posterPath} alt="Poster" />
        </div>

        <div className='title-text' >
          <span>{this.state.index}. </span><a href={this.state.titlePath}>{this.state.title}</a>
          <div className='rating-container'>
            <span className='rating-count'><img src={thumbsup} alt="ratingCount" style={{width: '8%'}} /> : {this.state.ratingCount}</span>
            <span className='ghost'> | </span>
            <span className='rating-value'><img src={star} alt="ratingValue" style={{width: '8%'}} /> : {this.state.ratingValue}</span>
          </div>
        </div>
      </div>
    )
  }
}


export default Poster;
