const express=require('express')
const router = express.Router()


router.get('/fetchBookTitle',async(req,res)=>{
    try{
        // display data from mongodb
    }
    catch(e){
        console.error(error.message);
        return res.status(500).send('Internal server error');
    }
})