import React from 'react';
import Poster from './Poster'; // Tell webpack this JS file uses this image
import './Poster.css';
import Title from './Title';
import './TitleBox.css';
import Container from '@material-ui/core/Container';
import Box from '@material-ui/core/Box';


function TitleBox() {
    return (
        <Container maxWidth='lg' >
            <Box className='title-box'>
                <Title />
                <div className='poster-row'>
                    <Poster dataFromParent = {0}/>
                    <Poster dataFromParent = {1}/>
                    <Poster dataFromParent = {2}/>
                    <Poster dataFromParent = {3}/>
                    <Poster dataFromParent = {4}/>
                </div>

                <div className='poster-row'>
                    <Poster dataFromParent = {5}/>
                    <Poster dataFromParent = {6}/>
                    <Poster dataFromParent = {7}/>
                    <Poster dataFromParent = {8}/>
                    <Poster dataFromParent = {9}/>
                </div>
            </Box>
        </Container>
    )
}

export default TitleBox;
